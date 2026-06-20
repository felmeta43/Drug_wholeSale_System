from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Customer, CustomerDocument
from .forms import CustomerForm, CustomerDocumentForm


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20

    def get_queryset(self):
        qs = Customer.objects.order_by('name')
        search = self.request.GET.get('search')
        customer_type = self.request.GET.get('type')
        region = self.request.GET.get('region')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(tin_number__icontains=search) |
                Q(phone__icontains=search) |
                Q(contact_person__icontains=search)
            )
        if customer_type:
            qs = qs.filter(customer_type=customer_type)
        if region:
            qs = qs.filter(region=region)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer_types'] = Customer.CUSTOMER_TYPES
        from customers.models import ETHIOPIAN_REGIONS
        context['regions'] = ETHIOPIAN_REGIONS
        context['total_customers'] = Customer.objects.filter(is_active=True).count()
        return context

    def get_template_names(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ['customers/_customer_results.html']
        return [self.template_name]


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer created successfully.')
        return super().form_valid(form)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'

    def get_success_url(self):
        return reverse_lazy('customer_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Customer updated successfully.')
        return super().form_valid(form)


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()
        context['sales_orders'] = self.object.sales_orders.order_by('-created_at')[:10]
        context['invoices'] = self.object.invoices.order_by('-created_at')[:10]
        context['outstanding_balance'] = self.object.get_outstanding_balance()
        return context


@login_required
def add_customer_document(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    form = CustomerDocumentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc = form.save(commit=False)
        doc.customer = customer
        doc.save()
        messages.success(request, 'Document uploaded successfully.')
        return redirect('customer_detail', pk=customer_pk)
    return render(request, 'customers/document_form.html', {'form': form, 'customer': customer})


@login_required
def delete_customer_document(request, pk):
    doc = get_object_or_404(CustomerDocument, pk=pk)
    customer_pk = doc.customer.pk
    doc.delete()
    messages.success(request, 'Document deleted.')
    return redirect('customer_detail', pk=customer_pk)
