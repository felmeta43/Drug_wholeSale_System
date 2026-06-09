from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Invoice, Payment, CreditNote
from .forms import InvoiceForm, PaymentForm, CreditNoteForm


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        qs = Invoice.objects.select_related('customer').order_by('-created_at')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        if search:
            qs = qs.filter(
                Q(invoice_number__icontains=search) | Q(customer__name__icontains=search)
            )
        if status:
            qs = qs.filter(payment_status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Invoice.PAYMENT_STATUS_CHOICES
        context['total_outstanding'] = Invoice.objects.filter(
            payment_status__in=['unpaid', 'partial', 'overdue']
        ).aggregate(total=Sum('balance_due'))['total'] or 0
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'

    def form_valid(self, form):
        invoice = form.save(commit=False)
        invoice.created_by = self.request.user
        invoice.balance_due = invoice.total_amount - invoice.amount_paid
        invoice.save()
        messages.success(self.request, f'Invoice {invoice.invoice_number} created successfully.')
        return redirect('invoice_detail', pk=invoice.pk)


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()
        context['payment_form'] = PaymentForm(initial={'invoice': self.object})
        context['credit_notes'] = self.object.credit_notes.all()
        if self.object.sales_order:
            context['order_items'] = self.object.sales_order.items.select_related(
                'product_variant__product'
            )
        return context


@login_required
def record_payment(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    form = PaymentForm(request.POST or None, initial={'invoice': invoice})
    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        payment.invoice = invoice
        payment.received_by = request.user
        payment.save()
        messages.success(request, f'Payment of ETB {payment.amount} recorded successfully.')
        return redirect('invoice_detail', pk=invoice_pk)
    return render(request, 'invoices/payment_form.html', {
        'form': form, 'invoice': invoice
    })


@login_required
def invoice_print(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    payments = invoice.payments.all()
    order_items = None
    if invoice.sales_order:
        order_items = invoice.sales_order.items.select_related('product_variant__product')
    return render(request, 'invoices/invoice_print.html', {
        'invoice': invoice,
        'payments': payments,
        'order_items': order_items,
    })


class CreditNoteListView(LoginRequiredMixin, ListView):
    model = CreditNote
    template_name = 'invoices/credit_note_list.html'
    context_object_name = 'credit_notes'
    paginate_by = 20

    def get_queryset(self):
        return CreditNote.objects.select_related('customer', 'invoice').order_by('-created_at')


class CreditNoteCreateView(LoginRequiredMixin, CreateView):
    model = CreditNote
    form_class = CreditNoteForm
    template_name = 'invoices/credit_note_form.html'
    success_url = reverse_lazy('credit_note_list')

    def form_valid(self, form):
        cn = form.save(commit=False)
        cn.created_by = self.request.user
        cn.save()
        messages.success(self.request, f'Credit note {cn.credit_note_number} created.')
        return redirect(self.success_url)


@login_required
def aged_receivables(request):
    today = timezone.now().date()
    from datetime import timedelta
    invoices = Invoice.objects.filter(
        payment_status__in=['unpaid', 'partial', 'overdue']
    ).select_related('customer').order_by('customer__name', 'due_date')

    aged_data = []
    for inv in invoices:
        days_overdue = (today - inv.due_date).days if today > inv.due_date else 0
        aged_data.append({
            'invoice': inv,
            'days_overdue': days_overdue,
            'bucket': (
                'current' if days_overdue == 0 else
                '1-30' if days_overdue <= 30 else
                '31-60' if days_overdue <= 60 else
                '61-90' if days_overdue <= 90 else
                '90+'
            )
        })

    return render(request, 'invoices/aged_receivables.html', {
        'aged_data': aged_data,
        'today': today,
    })
