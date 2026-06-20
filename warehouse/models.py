from django.db import models
from django.conf import settings


class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='managed_warehouses')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    has_cold_storage = models.BooleanField(default=False)
    cold_storage_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                                 help_text='Capacity in cubic meters')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_total_stock_value(self):
        from inventory.models import StockBatch
        from django.db.models import Sum, F
        result = StockBatch.objects.filter(warehouse=self).annotate(
            value=F('quantity_available') * F('purchase_price')
        ).aggregate(total=Sum('value'))
        return result['total'] or 0

    def get_total_items(self):
        from inventory.models import StockBatch
        from django.db.models import Sum
        result = StockBatch.objects.filter(warehouse=self).aggregate(
            total=Sum('quantity_available')
        )
        return result['total'] or 0


class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('pending', 'Pending'),       # direct/push transfer created by sender, not yet shipped — kept for backward compatibility
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    transfer_number = models.CharField(max_length=50, unique=True, blank=True)
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='transfers_out')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='transfers_in')
    transfer_date = models.DateField()
    received_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name='created_transfers')
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='received_transfers')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='requested_transfers')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='approved_transfers')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Stock Transfer'
        verbose_name_plural = 'Stock Transfers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transfer_number}: {self.from_warehouse} → {self.to_warehouse}"

    def save(self, *args, **kwargs):
        if not self.transfer_number:
            import datetime
            last = StockTransfer.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.transfer_number = f"TRF-{datetime.date.today().strftime('%Y%m')}-{num:04d}"
        super().save(*args, **kwargs)


class StockTransferItem(models.Model):
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name='items')
    batch = models.ForeignKey('inventory.StockBatch', on_delete=models.PROTECT, related_name='transfer_items',
                               null=True, blank=True)
    product_variant = models.ForeignKey('products.ProductVariant', on_delete=models.PROTECT,
                                         related_name='transfer_items')
    quantity_requested = models.PositiveIntegerField(default=0, blank=True)
    quantity_sent = models.PositiveIntegerField(default=0, blank=True)
    quantity_received = models.PositiveIntegerField(default=0, blank=True)
    notes = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'Stock Transfer Item'
        verbose_name_plural = 'Stock Transfer Items'

    def __str__(self):
        return f"{self.transfer.transfer_number} - {self.product_variant} x{self.quantity_sent}"
