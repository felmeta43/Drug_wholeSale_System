from django.contrib import admin
from .models import Warehouse, StockTransfer, StockTransferItem


class StockTransferItemInline(admin.TabularInline):
    model = StockTransferItem
    extra = 1
    fields = ['product_variant', 'batch', 'quantity_sent', 'quantity_received', 'notes']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'region', 'manager', 'has_cold_storage', 'is_active']
    list_filter = ['region', 'has_cold_storage', 'is_active']
    search_fields = ['name', 'code', 'city']


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_number', 'from_warehouse', 'to_warehouse', 'transfer_date', 'status', 'created_by']
    list_filter = ['status', 'transfer_date', 'from_warehouse', 'to_warehouse']
    search_fields = ['transfer_number']
    inlines = [StockTransferItemInline]
    date_hierarchy = 'transfer_date'
