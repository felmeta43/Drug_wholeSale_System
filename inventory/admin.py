from django.contrib import admin
from .models import StockBatch, StockMovement, StockAlert


@admin.register(StockBatch)
class StockBatchAdmin(admin.ModelAdmin):
    list_display = ['product_variant', 'warehouse', 'batch_number', 'quantity_available',
                    'expiry_date', 'purchase_price']
    list_filter = ['warehouse', 'expiry_date']
    search_fields = ['product_variant__product__name', 'batch_number', 'lot_number']
    date_hierarchy = 'created_at'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['batch', 'movement_type', 'quantity', 'reference_number', 'performed_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['batch__product_variant__product__name', 'reference_number']
    date_hierarchy = 'created_at'


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product_variant', 'warehouse', 'alert_type', 'current_value', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'is_resolved', 'warehouse']
    search_fields = ['product_variant__product__name']
