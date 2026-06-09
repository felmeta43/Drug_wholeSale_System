from django.db import models
from django.conf import settings
from products.models import ProductVariant


class StockBatch(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name='stock_batches')
    warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.PROTECT, related_name='stock_batches')
    batch_number = models.CharField(max_length=100)
    lot_number = models.CharField(max_length=100, blank=True)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    quantity_received = models.PositiveIntegerField(default=0)
    quantity_available = models.PositiveIntegerField(default=0)
    quantity_reserved = models.PositiveIntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='stock_batches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock Batch'
        verbose_name_plural = 'Stock Batches'
        ordering = ['expiry_date', 'batch_number']
        unique_together = ['product_variant', 'warehouse', 'batch_number']

    def __str__(self):
        return f"{self.product_variant} | Batch: {self.batch_number} | Qty: {self.quantity_available}"

    def is_expired(self):
        from django.utils import timezone
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    def days_to_expiry(self):
        from django.utils import timezone
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None

    def is_expiring_soon(self, days=90):
        days_left = self.days_to_expiry()
        if days_left is not None:
            return 0 <= days_left <= days
        return False


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('expired', 'Expired'),
        ('damaged', 'Damaged'),
    ]

    batch = models.ForeignKey(StockBatch, on_delete=models.PROTECT, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    from_warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='movements_out')
    to_warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='movements_in')
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                      related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.batch.product_variant} - Qty: {self.quantity}"


class StockAlert(models.Model):
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('expiry_warning', 'Expiry Warning'),
        ('expired', 'Expired'),
        ('out_of_stock', 'Out of Stock'),
    ]

    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='alerts')
    warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.CASCADE, related_name='alerts',
                                   null=True, blank=True)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_resolved = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Stock Alert'
        verbose_name_plural = 'Stock Alerts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.product_variant}"
