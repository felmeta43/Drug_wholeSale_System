from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['product_variant', 'quantity', 'unit_price', 'discount_percent', 'total_price',
              'received_quantity', 'batch_number', 'expiry_date']
    readonly_fields = ['total_price']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'warehouse', 'order_date', 'status', 'total_amount']
    list_filter = ['status', 'warehouse', 'order_date']
    search_fields = ['po_number', 'supplier__name']
    inlines = [PurchaseOrderItemInline]
    date_hierarchy = 'order_date'


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1
    fields = ['product_variant', 'batch', 'quantity', 'unit_price', 'discount_percent', 'total_price',
              'delivered_quantity']
    readonly_fields = ['total_price']


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'warehouse', 'order_date', 'status', 'total_amount']
    list_filter = ['status', 'warehouse', 'order_date']
    search_fields = ['order_number', 'customer__name']
    inlines = [SalesOrderItemInline]
    date_hierarchy = 'order_date'
