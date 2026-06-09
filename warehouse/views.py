from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, F
from .models import Warehouse, StockTransfer, StockTransferItem
from .forms import WarehouseForm, StockTransferForm, StockTransferItemFormSet


class WarehouseListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'warehouse/warehouse_list.html'
    context_object_name = 'warehouses'

    def get_queryset(self):
        return Warehouse.objects.filter(is_active=True).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for wh in context['warehouses']:
            wh.total_items = wh.get_total_items()
            wh.total_value = wh.get_total_stock_value()
        return context


class WarehouseCreateView(LoginRequiredMixin, CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'warehouse/warehouse_form.html'
    success_url = reverse_lazy('warehouse_list')

    def form_valid(self, form):
        messages.success(self.request, 'Warehouse created successfully.')
        return super().form_valid(form)


class WarehouseUpdateView(LoginRequiredMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'warehouse/warehouse_form.html'
    success_url = reverse_lazy('warehouse_list')

    def form_valid(self, form):
        messages.success(self.request, 'Warehouse updated successfully.')
        return super().form_valid(form)


class WarehouseDetailView(LoginRequiredMixin, DetailView):
    model = Warehouse
    template_name = 'warehouse/warehouse_detail.html'
    context_object_name = 'warehouse'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from inventory.models import StockBatch
        context['stock_batches'] = StockBatch.objects.filter(
            warehouse=self.object, quantity_available__gt=0
        ).select_related('product_variant__product').order_by('expiry_date')[:30]
        context['total_items'] = self.object.get_total_items()
        context['total_value'] = self.object.get_total_stock_value()
        return context


class StockTransferListView(LoginRequiredMixin, ListView):
    model = StockTransfer
    template_name = 'warehouse/transfer_list.html'
    context_object_name = 'transfers'
    paginate_by = 20

    def get_queryset(self):
        qs = StockTransfer.objects.select_related('from_warehouse', 'to_warehouse').order_by('-created_at')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = StockTransfer.STATUS_CHOICES
        return context


@login_required
def stock_transfer_create(request):
    form = StockTransferForm(request.POST or None)
    formset = StockTransferItemFormSet(request.POST or None)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        transfer = form.save(commit=False)
        transfer.created_by = request.user
        transfer.save()
        formset.instance = transfer
        formset.save()
        messages.success(request, f'Transfer {transfer.transfer_number} created.')
        return redirect('transfer_detail', pk=transfer.pk)
    return render(request, 'warehouse/transfer_form.html', {'form': form, 'formset': formset})


class StockTransferDetailView(LoginRequiredMixin, DetailView):
    model = StockTransfer
    template_name = 'warehouse/transfer_detail.html'
    context_object_name = 'transfer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product_variant__product', 'batch')
        return context


@login_required
def complete_transfer(request, pk):
    transfer = get_object_or_404(StockTransfer, pk=pk)
    if request.method == 'POST':
        import datetime
        from inventory.models import StockBatch, StockMovement
        for item in transfer.items.all():
            received_qty = int(request.POST.get(f'received_{item.pk}', 0))
            if received_qty > 0:
                # Deduct from source batch
                item.batch.quantity_available -= received_qty
                item.batch.save()
                # Create movement for outgoing
                StockMovement.objects.create(
                    batch=item.batch,
                    movement_type='transfer',
                    from_warehouse=transfer.from_warehouse,
                    to_warehouse=transfer.to_warehouse,
                    quantity=received_qty,
                    reference_number=transfer.transfer_number,
                    performed_by=request.user,
                    reason=f'Transfer {transfer.transfer_number}'
                )
                # Create new batch in destination warehouse
                new_batch = StockBatch.objects.create(
                    product_variant=item.product_variant,
                    warehouse=transfer.to_warehouse,
                    batch_number=item.batch.batch_number,
                    lot_number=item.batch.lot_number,
                    manufacture_date=item.batch.manufacture_date,
                    expiry_date=item.batch.expiry_date,
                    quantity_received=received_qty,
                    quantity_available=received_qty,
                    purchase_price=item.batch.purchase_price,
                    supplier=item.batch.supplier
                )
                StockMovement.objects.create(
                    batch=new_batch,
                    movement_type='in',
                    from_warehouse=transfer.from_warehouse,
                    to_warehouse=transfer.to_warehouse,
                    quantity=received_qty,
                    reference_number=transfer.transfer_number,
                    performed_by=request.user,
                    reason=f'Received from transfer {transfer.transfer_number}'
                )
                item.quantity_received = received_qty
                item.save()

        transfer.status = 'completed'
        transfer.received_date = datetime.date.today()
        transfer.received_by = request.user
        transfer.save()
        messages.success(request, 'Transfer completed successfully.')
        return redirect('transfer_detail', pk=pk)
    return render(request, 'warehouse/complete_transfer.html', {
        'transfer': transfer,
        'items': transfer.items.select_related('product_variant__product', 'batch')
    })
