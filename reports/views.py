from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count, F, Q
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta, date
import json


def admin_required(view_func):
    """Gate admin-only report pages the same way core.views.company_settings does."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
            messages.error(request, 'You do not have permission to view this page.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    expiry_limit = today + timedelta(days=90)

    # Counts
    from products.models import Product, ProductVariant
    from customers.models import Customer
    from suppliers.models import Supplier
    from orders.models import SalesOrder, PurchaseOrder
    from invoices.models import Invoice
    from inventory.models import StockBatch, StockAlert
    from warehouse.models import Warehouse

    total_products = Product.objects.filter(is_active=True).count()
    total_customers = Customer.objects.filter(is_active=True).count()
    total_suppliers = Supplier.objects.filter(is_active=True).count()
    total_warehouses = Warehouse.objects.filter(is_active=True).count()

    # Orders this month
    monthly_sales = SalesOrder.objects.filter(
        order_date__gte=month_start,
        status__in=['confirmed', 'processing', 'partial', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    monthly_orders_count = SalesOrder.objects.filter(order_date__gte=month_start).count()

    # Outstanding invoices
    outstanding = Invoice.objects.filter(
        payment_status__in=['unpaid', 'partial', 'overdue']
    ).aggregate(total=Sum('balance_due'))['total'] or 0

    # Alerts
    low_stock_count = StockAlert.objects.filter(alert_type='low_stock', is_resolved=False).count()
    expiring_count = StockBatch.objects.filter(
        expiry_date__lte=expiry_limit, expiry_date__gte=today, quantity_available__gt=0
    ).count()
    expired_count = StockBatch.objects.filter(
        expiry_date__lt=today, quantity_available__gt=0
    ).count()

    # Recent orders
    recent_sales_orders = SalesOrder.objects.select_related('customer').order_by('-created_at')[:8]
    recent_purchase_orders = PurchaseOrder.objects.select_related('supplier').order_by('-created_at')[:5]

    # Monthly sales chart data (last 6 months)
    chart_labels = []
    chart_data = []
    for i in range(5, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        month_start_i = month_date.replace(day=1)
        if month_date.month == 12:
            month_end_i = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            month_end_i = month_date.replace(month=month_date.month + 1, day=1)
        month_total = SalesOrder.objects.filter(
            order_date__gte=month_start_i,
            order_date__lt=month_end_i,
            status__in=['confirmed', 'processing', 'partial', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        chart_labels.append(month_date.strftime('%b %Y'))
        chart_data.append(float(month_total))

    # Top products by sales
    from orders.models import SalesOrderItem
    top_products = SalesOrderItem.objects.filter(
        sales_order__order_date__gte=month_start
    ).values(
        'product_variant__product__name'
    ).annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_revenue')[:5]

    # Recent invoices
    recent_invoices = Invoice.objects.filter(
        payment_status__in=['unpaid', 'overdue']
    ).select_related('customer').order_by('due_date')[:5]

    # Pending POs
    pending_pos = PurchaseOrder.objects.filter(
        status__in=['submitted', 'approved']
    ).select_related('supplier').count()

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_suppliers': total_suppliers,
        'total_warehouses': total_warehouses,
        'monthly_sales': monthly_sales,
        'monthly_orders_count': monthly_orders_count,
        'outstanding': outstanding,
        'low_stock_count': low_stock_count,
        'expiring_count': expiring_count,
        'expired_count': expired_count,
        'recent_sales_orders': recent_sales_orders,
        'recent_purchase_orders': recent_purchase_orders,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'top_products': top_products,
        'recent_invoices': recent_invoices,
        'pending_pos': pending_pos,
        'today': today,
    }
    return render(request, 'dashboard.html', context)


@login_required
def sales_report(request):
    from orders.models import SalesOrder, SalesOrderItem
    period = request.GET.get('period', 'monthly')
    today = timezone.now().date()

    if period == 'daily':
        start_date = today
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
    elif period == 'monthly':
        start_date = today.replace(day=1)
    elif period == 'yearly':
        start_date = today.replace(month=1, day=1)
    else:
        start_date = today.replace(day=1)

    orders = SalesOrder.objects.filter(
        order_date__gte=start_date,
        status__in=['confirmed', 'processing', 'partial', 'delivered']
    ).select_related('customer', 'warehouse').order_by('-order_date')

    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_vat = orders.aggregate(total=Sum('vat_amount'))['total'] or 0
    total_orders = orders.count()

    top_customers = orders.values(
        'customer__name'
    ).annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('-total')[:10]

    return render(request, 'reports/sales_report.html', {
        'orders': orders[:50],
        'total_revenue': total_revenue,
        'total_vat': total_vat,
        'total_orders': total_orders,
        'top_customers': top_customers,
        'period': period,
        'start_date': start_date,
    })


@login_required
def inventory_report(request):
    from inventory.models import StockBatch
    from warehouse.models import Warehouse

    warehouses = Warehouse.objects.filter(is_active=True)
    selected_warehouse = request.GET.get('warehouse')

    batches = StockBatch.objects.filter(quantity_available__gt=0).select_related(
        'product_variant__product__category', 'warehouse'
    )
    if selected_warehouse:
        batches = batches.filter(warehouse_id=selected_warehouse)

    total_value = batches.annotate(
        val=F('quantity_available') * F('purchase_price')
    ).aggregate(total=Sum('val'))['total'] or 0

    total_items = batches.aggregate(total=Sum('quantity_available'))['total'] or 0

    # By category
    from products.models import Category
    category_stock = batches.values(
        'product_variant__product__category__name'
    ).annotate(
        total_qty=Sum('quantity_available'),
        total_val=Sum(F('quantity_available') * F('purchase_price'))
    ).order_by('-total_val')

    return render(request, 'reports/inventory_report.html', {
        'batches': batches.order_by('product_variant__product__name')[:50],
        'warehouses': warehouses,
        'selected_warehouse': selected_warehouse,
        'total_value': total_value,
        'total_items': total_items,
        'category_stock': category_stock,
    })


@login_required
def customer_report(request):
    from customers.models import Customer
    from orders.models import SalesOrder
    from invoices.models import Invoice
    from django.db.models import Sum, Count

    customers = Customer.objects.filter(is_active=True).annotate(
        total_orders=Count('sales_orders'),
        total_revenue=Sum('sales_orders__total_amount')
    ).order_by('-total_revenue')

    top_customers = customers[:20]
    total_customers = Customer.objects.filter(is_active=True).count()

    return render(request, 'reports/customer_report.html', {
        'customers': top_customers,
        'total_customers': total_customers,
    })


@login_required
def supplier_report(request):
    from suppliers.models import Supplier
    from orders.models import PurchaseOrder
    from django.db.models import Sum, Count

    suppliers = Supplier.objects.filter(is_active=True).annotate(
        total_pos=Count('purchase_orders'),
        total_purchased=Sum('purchase_orders__total_amount')
    ).order_by('-total_purchased')

    return render(request, 'reports/supplier_report.html', {
        'suppliers': suppliers,
    })


@login_required
def financial_summary(request):
    from invoices.models import Invoice, Payment
    from orders.models import SalesOrder, PurchaseOrder
    today = timezone.now().date()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    monthly_revenue = Invoice.objects.filter(
        invoice_date__gte=month_start,
        payment_status__in=['paid', 'partial']
    ).aggregate(total=Sum('amount_paid'))['total'] or 0

    yearly_revenue = Invoice.objects.filter(
        invoice_date__gte=year_start
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    total_outstanding = Invoice.objects.filter(
        payment_status__in=['unpaid', 'partial', 'overdue']
    ).aggregate(total=Sum('balance_due'))['total'] or 0

    monthly_purchases = PurchaseOrder.objects.filter(
        order_date__gte=month_start,
        status='received'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Monthly payment breakdown
    payment_methods = Payment.objects.filter(
        payment_date__gte=month_start
    ).values('payment_method').annotate(total=Sum('amount')).order_by('-total')

    return render(request, 'reports/financial_summary.html', {
        'monthly_revenue': monthly_revenue,
        'yearly_revenue': yearly_revenue,
        'total_outstanding': total_outstanding,
        'monthly_purchases': monthly_purchases,
        'payment_methods': payment_methods,
        'today': today,
    })


@login_required
def expiry_report_page(request):
    from inventory.models import StockBatch
    today = timezone.now().date()
    expiry_limit = today + timedelta(days=90)

    expiring_soon = StockBatch.objects.filter(
        expiry_date__lte=expiry_limit,
        expiry_date__gte=today,
        quantity_available__gt=0
    ).select_related('product_variant__product', 'warehouse').order_by('expiry_date')

    expired = StockBatch.objects.filter(
        expiry_date__lt=today,
        quantity_available__gt=0
    ).select_related('product_variant__product', 'warehouse').order_by('expiry_date')

    return render(request, 'reports/expiry_report.html', {
        'expiring_soon': expiring_soon,
        'expired': expired,
        'today': today,
    })


@login_required
def stock_balance_report(request):
    """Current stock balance per product/warehouse, with a link into the
    bin card for the full transaction history behind each row."""
    from inventory.models import StockBatch
    from warehouse.models import Warehouse

    warehouses = Warehouse.objects.filter(is_active=True)
    selected_warehouse = request.GET.get('warehouse')
    search = request.GET.get('search')

    balances = StockBatch.objects.values(
        'product_variant_id', 'product_variant__product__name',
        'product_variant__strength', 'product_variant__packaging',
        'warehouse_id', 'warehouse__name',
    ).annotate(
        qty_available=Sum('quantity_available'),
        qty_reserved=Sum('quantity_reserved'),
        stock_value=Sum(F('quantity_available') * F('purchase_price')),
    ).order_by('product_variant__product__name', 'warehouse__name')

    if selected_warehouse:
        balances = balances.filter(warehouse_id=selected_warehouse)
    if search:
        balances = balances.filter(
            Q(product_variant__product__name__icontains=search) |
            Q(product_variant__sku__icontains=search)
        )

    total_value = sum((b['stock_value'] or 0) for b in balances)

    paginator = Paginator(list(balances), 30)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'reports/stock_balance.html', {
        'page_obj': page_obj,
        'rows': page_obj.object_list,
        'warehouses': warehouses,
        'selected_warehouse': selected_warehouse,
        'search': search,
        'total_value': total_value,
    })


def _movement_delta(movement):
    """StockMovement.quantity is signed for every movement type except
    'transfer', which is always recorded against the sending batch with a
    positive quantity even though it decreases that batch's stock (see
    warehouse/views.py) — so transfers need their sign flipped here."""
    return -movement.quantity if movement.movement_type == 'transfer' else movement.quantity


@login_required
def bin_card_report(request):
    """Per-item, per-warehouse ledger: every stock movement for a product
    variant with a running balance, the way a paper bin card would show it."""
    from inventory.models import StockMovement
    from products.models import ProductVariant
    from warehouse.models import Warehouse

    variant_id = request.GET.get('variant')
    warehouse_id = request.GET.get('warehouse')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    variant = ProductVariant.objects.filter(pk=variant_id).select_related('product').first() if variant_id else None
    warehouse = Warehouse.objects.filter(pk=warehouse_id).first() if warehouse_id else None

    rows = []
    opening_balance = 0
    closing_balance = 0

    if variant:
        qs = StockMovement.objects.filter(batch__product_variant=variant).select_related(
            'batch', 'performed_by', 'from_warehouse', 'to_warehouse'
        )
        if warehouse:
            qs = qs.filter(batch__warehouse=warehouse)

        if date_from:
            opening_balance = sum(
                _movement_delta(m) for m in qs.filter(created_at__date__lt=date_from)
            )
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        balance = opening_balance
        for m in qs.order_by('created_at', 'id'):
            delta = _movement_delta(m)
            balance += delta
            rows.append({'movement': m, 'delta': delta, 'balance': balance})
        closing_balance = balance

    return render(request, 'reports/bin_card.html', {
        'variants': ProductVariant.objects.select_related('product').order_by('product__name', 'strength')[:500],
        'warehouses': Warehouse.objects.filter(is_active=True),
        'variant': variant,
        'warehouse': warehouse,
        'date_from': date_from,
        'date_to': date_to,
        'rows': rows,
        'opening_balance': opening_balance,
        'closing_balance': closing_balance,
    })


@admin_required
def audit_report(request):
    """Who created/updated/deleted what, and login activity, across the system."""
    from django.contrib.auth import get_user_model
    from django.contrib.contenttypes.models import ContentType
    from core.models import AuditLog

    User = get_user_model()
    qs = AuditLog.objects.select_related('actor', 'content_type').order_by('-created_at')

    actor_id = request.GET.get('actor')
    action = request.GET.get('action')
    model_id = request.GET.get('model')
    search = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if actor_id:
        qs = qs.filter(actor_id=actor_id)
    if action:
        qs = qs.filter(action=action)
    if model_id:
        qs = qs.filter(content_type_id=model_id)
    if search:
        qs = qs.filter(object_repr__icontains=search)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    paginator = Paginator(qs, 50)
    page_obj = paginator.get_page(request.GET.get('page'))

    tracked_content_types = ContentType.objects.filter(
        pk__in=AuditLog.objects.exclude(content_type__isnull=True)
        .values_list('content_type_id', flat=True).distinct()
    )

    return render(request, 'reports/audit_report.html', {
        'page_obj': page_obj,
        'logs': page_obj.object_list,
        'users': User.objects.order_by('username'),
        'action_choices': AuditLog.ACTION_CHOICES,
        'content_types': tracked_content_types,
        'selected_actor': actor_id,
        'selected_action': action,
        'selected_model': model_id,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
    })
