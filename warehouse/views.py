from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Sum, F
from django.utils import timezone
from .models import Warehouse, StockTransfer, StockTransferItem
from .forms import (
    WarehouseForm, StockTransferForm, StockTransferItemFormSet,
    StockTransferRequestForm, StockTransferRequestItemFormSet,
    StockTransferApproveItemFormSet, StockTransferReceiveItemFormSet,
)
from notifications.utils import notify


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
    """Direct/push transfer: sender already knows what they're shipping
    (batch + quantity_sent chosen directly), so it ships immediately —
    no separate approval step is needed on top of this. It still notifies
    the receiver and must go through 'receiver approves received items'
    before it's marked completed."""
    form = StockTransferForm(request.POST or None)
    formset = StockTransferItemFormSet(request.POST or None)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        from inventory.models import StockMovement
        transfer = form.save(commit=False)
        transfer.created_by = request.user
        transfer.status = 'in_transit'
        transfer.approved_by = request.user
        transfer.approved_at = timezone.now()
        transfer.save()
        formset.instance = transfer
        items = formset.save()

        for item in items:
            if item.batch and item.quantity_sent:
                item.batch.quantity_available -= item.quantity_sent
                item.batch.save()
                StockMovement.objects.create(
                    batch=item.batch,
                    movement_type='transfer',
                    from_warehouse=transfer.from_warehouse,
                    to_warehouse=transfer.to_warehouse,
                    quantity=item.quantity_sent,
                    reference_number=transfer.transfer_number,
                    performed_by=request.user,
                    reason=f'Transfer {transfer.transfer_number}'
                )

        notify(
            transfer.to_warehouse.manager,
            f"{transfer.from_warehouse.name} is sending you a stock transfer ({transfer.transfer_number}).",
            reverse('transfer_detail', args=[transfer.pk])
        )
        messages.success(request, f'Transfer {transfer.transfer_number} created and shipped.')
        return redirect('transfer_detail', pk=transfer.pk)
    return render(request, 'warehouse/transfer_form.html', {'form': form, 'formset': formset})


@login_required
def stock_transfer_request_create(request):
    """Pull request: initiated by the RECEIVING warehouse asking the sender
    to ship stock. Sender must approve the request (choosing batches) before
    it ships."""
    form = StockTransferRequestForm(request.POST or None)
    formset = StockTransferRequestItemFormSet(request.POST or None)
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        transfer = form.save(commit=False)
        transfer.created_by = request.user
        transfer.requested_by = request.user
        transfer.status = 'requested'
        transfer.save()
        formset.instance = transfer
        formset.save()

        notify(
            transfer.from_warehouse.manager,
            f"{transfer.to_warehouse.name} requested a stock transfer ({transfer.transfer_number}).",
            reverse('transfer_detail', args=[transfer.pk])
        )
        messages.success(request, f'Transfer request {transfer.transfer_number} submitted.')
        return redirect('transfer_detail', pk=transfer.pk)
    return render(request, 'warehouse/transfer_request_form.html', {'form': form, 'formset': formset})


class StockTransferDetailView(LoginRequiredMixin, DetailView):
    model = StockTransfer
    template_name = 'warehouse/transfer_detail.html'
    context_object_name = 'transfer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product_variant__product', 'batch')
        return context


@login_required
def stock_transfer_approve_request(request, pk):
    """Sender approves a receiver-initiated transfer request: chooses the
    source batch and quantity to ship for each requested item. Approving
    ships the transfer (status -> in_transit)."""
    transfer = get_object_or_404(StockTransfer, pk=pk, status='requested')
    from inventory.models import StockMovement

    def build_formset(data=None):
        fs = StockTransferApproveItemFormSet(data, instance=transfer)
        for form in fs.forms:
            form.fields['batch'].queryset = form.fields['batch'].queryset.model.objects.filter(
                product_variant_id=form.instance.product_variant_id,
                warehouse=transfer.from_warehouse,
                quantity_available__gt=0
            )
        return fs

    if request.method == 'POST':
        formset = build_formset(request.POST)
        if formset.is_valid():
            items = formset.save()
            for item in items:
                if item.batch and item.quantity_sent:
                    item.batch.quantity_available -= item.quantity_sent
                    item.batch.save()
                    StockMovement.objects.create(
                        batch=item.batch,
                        movement_type='transfer',
                        from_warehouse=transfer.from_warehouse,
                        to_warehouse=transfer.to_warehouse,
                        quantity=item.quantity_sent,
                        reference_number=transfer.transfer_number,
                        performed_by=request.user,
                        reason=f'Transfer {transfer.transfer_number}'
                    )

            transfer.status = 'in_transit'
            transfer.approved_by = request.user
            transfer.approved_at = timezone.now()
            transfer.save()

            notify(
                transfer.requested_by or transfer.to_warehouse.manager,
                f"Your transfer request {transfer.transfer_number} was approved and shipped.",
                reverse('transfer_detail', args=[transfer.pk])
            )
            messages.success(request, f'Transfer {transfer.transfer_number} approved and shipped.')
            return redirect('transfer_detail', pk=transfer.pk)
    else:
        formset = build_formset()

    return render(request, 'warehouse/transfer_approve_request.html', {
        'transfer': transfer,
        'formset': formset,
    })


@login_required
def complete_transfer(request, pk):
    """Receiver approves/confirms the received items, completing the transfer."""
    transfer = get_object_or_404(StockTransfer, pk=pk, status='in_transit')
    formset = StockTransferReceiveItemFormSet(request.POST or None, instance=transfer)
    if request.method == 'POST' and formset.is_valid():
        import datetime
        from inventory.models import StockBatch, StockMovement
        items = formset.save()
        for item in items:
            received_qty = item.quantity_received
            if received_qty > 0:
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

        transfer.status = 'completed'
        transfer.received_date = datetime.date.today()
        transfer.received_by = request.user
        transfer.save()

        notify(
            transfer.approved_by or transfer.created_by,
            f"{transfer.to_warehouse.name} confirmed receipt of transfer {transfer.transfer_number}.",
            reverse('transfer_detail', args=[transfer.pk])
        )
        messages.success(request, 'Transfer completed successfully.')
        return redirect('transfer_detail', pk=pk)
    return render(request, 'warehouse/complete_transfer.html', {
        'transfer': transfer,
        'formset': formset,
    })
