from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, F
from django.utils import timezone
from datetime import timedelta
from .models import StockBatch, StockMovement, StockAlert
from .forms import StockBatchForm, StockMovementForm, StockAdjustmentForm


class StockOverviewView(LoginRequiredMixin, ListView):
    model = StockBatch
    template_name = 'inventory/stock_overview.html'
    context_object_name = 'batches'
    paginate_by = 30

    def get_queryset(self):
        qs = StockBatch.objects.select_related(
            'product_variant__product', 'warehouse'
        ).order_by('expiry_date')
        warehouse = self.request.GET.get('warehouse')
        search = self.request.GET.get('search')
        expiry_filter = self.request.GET.get('expiry')
        if warehouse:
            qs = qs.filter(warehouse_id=warehouse)
        if search:
            qs = qs.filter(
                Q(product_variant__product__name__icontains=search) |
                Q(batch_number__icontains=search)
            )
        if expiry_filter == 'expiring_soon':
            limit_date = timezone.now().date() + timedelta(days=90)
            qs = qs.filter(expiry_date__lte=limit_date, expiry_date__gte=timezone.now().date())
        elif expiry_filter == 'expired':
            qs = qs.filter(expiry_date__lt=timezone.now().date())
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from warehouse.models import Warehouse
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        today = timezone.now().date()
        expiry_limit = today + timedelta(days=90)
        context['expiring_count'] = StockBatch.objects.filter(
            expiry_date__lte=expiry_limit, expiry_date__gte=today, quantity_available__gt=0
        ).count()
        context['expired_count'] = StockBatch.objects.filter(
            expiry_date__lt=today, quantity_available__gt=0
        ).count()
        context['total_value'] = StockBatch.objects.filter(quantity_available__gt=0).annotate(
            val=F('quantity_available') * F('purchase_price')
        ).aggregate(total=Sum('val'))['total'] or 0
        return context


class StockBatchCreateView(LoginRequiredMixin, CreateView):
    model = StockBatch
    form_class = StockBatchForm
    template_name = 'inventory/batch_form.html'
    success_url = reverse_lazy('stock_overview')

    def form_valid(self, form):
        batch = form.save(commit=False)
        batch.save()
        StockMovement.objects.create(
            batch=batch,
            movement_type='in',
            to_warehouse=batch.warehouse,
            quantity=batch.quantity_received,
            unit_price=batch.purchase_price,
            performed_by=self.request.user,
            reason='Initial stock in'
        )
        messages.success(self.request, 'Stock batch created successfully.')
        return redirect(self.success_url)


class StockBatchUpdateView(LoginRequiredMixin, UpdateView):
    model = StockBatch
    form_class = StockBatchForm
    template_name = 'inventory/batch_form.html'
    success_url = reverse_lazy('stock_overview')

    def form_valid(self, form):
        messages.success(self.request, 'Batch updated successfully.')
        return super().form_valid(form)


class StockBatchDetailView(LoginRequiredMixin, DetailView):
    model = StockBatch
    template_name = 'inventory/batch_detail.html'
    context_object_name = 'batch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movements'] = self.object.movements.order_by('-created_at')[:20]
        return context


class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = 'inventory/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 30

    def get_queryset(self):
        qs = StockMovement.objects.select_related(
            'batch__product_variant__product', 'performed_by'
        ).order_by('-created_at')
        movement_type = self.request.GET.get('type')
        search = self.request.GET.get('search')
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        if search:
            qs = qs.filter(
                Q(batch__product_variant__product__name__icontains=search) |
                Q(reference_number__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movement_types'] = StockMovement.MOVEMENT_TYPES
        return context


@login_required
def stock_adjustment(request):
    form = StockAdjustmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        batch = form.cleaned_data['batch']
        adjustment_type = form.cleaned_data['adjustment_type']
        quantity = form.cleaned_data['quantity']
        reason = form.cleaned_data['reason']
        reference = form.cleaned_data.get('reference_number', '')

        if adjustment_type == 'add':
            batch.quantity_available += quantity
            movement_qty = quantity
        else:
            if quantity > batch.quantity_available:
                messages.error(request, 'Adjustment quantity exceeds available stock.')
                return render(request, 'inventory/stock_adjustment.html', {'form': form})
            batch.quantity_available -= quantity
            movement_qty = -quantity

        batch.save()
        StockMovement.objects.create(
            batch=batch,
            movement_type='adjustment',
            quantity=movement_qty,
            reference_number=reference,
            reason=reason,
            performed_by=request.user
        )
        messages.success(request, f'Stock adjusted by {quantity} units.')
        return redirect('stock_overview')
    return render(request, 'inventory/stock_adjustment.html', {'form': form})


class AlertListView(LoginRequiredMixin, ListView):
    model = StockAlert
    template_name = 'inventory/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 30

    def get_queryset(self):
        return StockAlert.objects.filter(is_resolved=False).select_related(
            'product_variant__product', 'warehouse'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alert_types'] = StockAlert.ALERT_TYPES
        return context


@login_required
def resolve_alert(request, pk):
    alert = get_object_or_404(StockAlert, pk=pk)
    alert.is_resolved = True
    alert.resolved_at = timezone.now()
    alert.save()
    messages.success(request, 'Alert resolved.')
    return redirect('alert_list')


@login_required
def expiry_report(request):
    today = timezone.now().date()
    expiry_limit = today + timedelta(days=90)
    expiring = StockBatch.objects.filter(
        expiry_date__lte=expiry_limit,
        expiry_date__gte=today,
        quantity_available__gt=0
    ).select_related('product_variant__product', 'warehouse').order_by('expiry_date')

    expired = StockBatch.objects.filter(
        expiry_date__lt=today,
        quantity_available__gt=0
    ).select_related('product_variant__product', 'warehouse').order_by('expiry_date')

    return render(request, 'inventory/expiry_report.html', {
        'expiring': expiring,
        'expired': expired,
        'today': today,
    })
