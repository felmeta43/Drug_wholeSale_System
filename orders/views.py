from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem
from .forms import (PurchaseOrderForm, PurchaseOrderItemFormSet,
                    SalesOrderForm, SalesOrderItemFormSet)


class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'orders/purchase_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        qs = PurchaseOrder.objects.select_related('supplier', 'warehouse').order_by('-created_at')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        if search:
            qs = qs.filter(
                Q(po_number__icontains=search) | Q(supplier__name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PurchaseOrder.STATUS_CHOICES
        return context


@login_required
def purchase_order_create(request):
    from products.models import ProductVariant
    form = PurchaseOrderForm(request.POST or None)
    formset = PurchaseOrderItemFormSet(request.POST or None)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        order = form.save(commit=False)
        order.created_by = request.user
        order.save()
        formset.instance = order
        formset.save()
        order.calculate_total()
        messages.success(request, f'Purchase Order {order.po_number} created successfully.')
        return redirect('purchase_order_detail', pk=order.pk)
    variants = ProductVariant.objects.filter(is_active=True).select_related('product').order_by('product__name')
    return render(request, 'orders/purchase_order_form.html', {
        'form': form,
        'formset': formset,
        'variants': variants,
        'title': 'Create Purchase Order',
    })


class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'orders/purchase_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product_variant__product')
        return context


@login_required
def purchase_order_update_status(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(PurchaseOrder.STATUS_CHOICES):
        order.status = new_status
        if new_status == 'approved':
            order.approved_by = request.user
        order.save()
        messages.success(request, f'Order status updated to {order.get_status_display()}.')
    return redirect('purchase_order_detail', pk=pk)


@login_required
def receive_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        from inventory.models import StockBatch, StockMovement
        import datetime
        for item in order.items.all():
            received_qty = int(request.POST.get(f'received_{item.pk}', 0))
            if received_qty > 0:
                batch_number = item.batch_number or f"BATCH-{order.po_number}-{item.pk}"
                batch = StockBatch.objects.create(
                    product_variant=item.product_variant,
                    warehouse=order.warehouse,
                    batch_number=batch_number,
                    expiry_date=item.expiry_date,
                    quantity_received=received_qty,
                    quantity_available=received_qty,
                    purchase_price=item.unit_price,
                    supplier=order.supplier
                )
                StockMovement.objects.create(
                    batch=batch,
                    movement_type='in',
                    to_warehouse=order.warehouse,
                    quantity=received_qty,
                    unit_price=item.unit_price,
                    reference_number=order.po_number,
                    performed_by=request.user,
                    reason=f'Received from PO {order.po_number}'
                )
                item.received_quantity = received_qty
                item.save()
        import datetime
        order.status = 'received'
        order.received_date = datetime.date.today()
        order.save()
        messages.success(request, 'Purchase order received and stock updated.')
        return redirect('purchase_order_detail', pk=pk)
    return render(request, 'orders/receive_purchase_order.html', {
        'order': order,
        'items': order.items.select_related('product_variant__product')
    })


class SalesOrderListView(LoginRequiredMixin, ListView):
    model = SalesOrder
    template_name = 'orders/sales_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        qs = SalesOrder.objects.select_related('customer', 'warehouse').order_by('-created_at')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        if search:
            qs = qs.filter(
                Q(order_number__icontains=search) | Q(customer__name__icontains=search)
            )
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = SalesOrder.STATUS_CHOICES
        return context


@login_required
def sales_order_create(request):
    from products.models import ProductVariant
    form = SalesOrderForm(request.POST or None)
    formset = SalesOrderItemFormSet(request.POST or None)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        order = form.save(commit=False)
        order.created_by = request.user
        action = request.POST.get('action', 'save')
        if action == 'confirm':
            order.status = 'confirmed'
            order.approved_by = request.user
        order.save()
        formset.instance = order
        formset.save()
        order.calculate_totals()
        messages.success(request, f'Sales Order {order.order_number} created successfully.')
        return redirect('sales_order_detail', pk=order.pk)
    variants = ProductVariant.objects.filter(is_active=True).select_related('product').order_by('product__name')
    return render(request, 'orders/sales_order_form.html', {
        'form': form,
        'formset': formset,
        'variants': variants,
        'title': 'Create Sales Order',
    })


@login_required
def sales_order_edit(request, pk):
    from products.models import ProductVariant
    order = get_object_or_404(SalesOrder, pk=pk)
    form = SalesOrderForm(request.POST or None, instance=order)
    formset = SalesOrderItemFormSet(request.POST or None, instance=order)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        order = form.save(commit=False)
        action = request.POST.get('action', 'save')
        if action == 'confirm' and order.status == 'draft':
            order.status = 'confirmed'
            order.approved_by = request.user
        order.save()
        formset.instance = order
        formset.save()
        order.calculate_totals()
        messages.success(request, f'Sales Order {order.order_number} updated.')
        return redirect('sales_order_detail', pk=order.pk)
    variants = ProductVariant.objects.filter(is_active=True).select_related('product').order_by('product__name')
    return render(request, 'orders/sales_order_form.html', {
        'form': form,
        'formset': formset,
        'variants': variants,
        'order': order,
        'title': f'Edit {order.order_number}',
    })


class SalesOrderDetailView(LoginRequiredMixin, DetailView):
    model = SalesOrder
    template_name = 'orders/sales_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product_variant__product', 'batch')
        return context


@login_required
def sales_order_update_status(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(SalesOrder.STATUS_CHOICES):
        order.status = new_status
        if new_status == 'confirmed':
            order.approved_by = request.user
        order.save()
        messages.success(request, f'Order status updated to {order.get_status_display()}.')
    return redirect('sales_order_detail', pk=pk)


@login_required
def generate_invoice_from_order(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    if hasattr(order, 'invoice'):
        messages.warning(request, 'Invoice already exists for this order.')
        return redirect('invoice_detail', pk=order.invoice.pk)
    import datetime
    from invoices.models import Invoice
    due_date = datetime.date.today() + datetime.timedelta(days=order.payment_terms)
    invoice = Invoice.objects.create(
        sales_order=order,
        customer=order.customer,
        due_date=due_date,
        subtotal=order.subtotal,
        discount_amount=order.discount_amount,
        vat_amount=order.vat_amount,
        total_amount=order.total_amount,
        balance_due=order.total_amount,
        created_by=request.user
    )
    messages.success(request, f'Invoice {invoice.invoice_number} generated successfully.')
    return redirect('invoice_detail', pk=invoice.pk)
