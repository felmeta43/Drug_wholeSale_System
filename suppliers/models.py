from django.db import models


class Supplier(models.Model):
    SUPPLIER_TYPES = [
        ('local_manufacturer', 'Local Manufacturer'),
        ('importer', 'Importer'),
        ('distributor', 'Distributor'),
        ('agent', 'Agent'),
        ('international', 'International Supplier'),
    ]

    name = models.CharField(max_length=300)
    supplier_type = models.CharField(max_length=30, choices=SUPPLIER_TYPES, default='distributor')
    tin_number = models.CharField(max_length=50, blank=True, verbose_name='TIN Number')
    business_license_number = models.CharField(max_length=100, blank=True)
    efda_license_number = models.CharField(max_length=100, blank=True, verbose_name='EFDA License Number')
    contact_person = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    alt_phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Ethiopia')
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    payment_terms = models.PositiveIntegerField(default=30, help_text='Payment terms in days')
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    bank_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_supplier_type_display()})"

    def get_total_purchase_orders(self):
        return self.purchase_orders.count()

    def get_total_purchased(self):
        from orders.models import PurchaseOrder
        from django.db.models import Sum
        result = self.purchase_orders.filter(
            status__in=['received', 'approved']
        ).aggregate(total=Sum('total_amount'))
        return result['total'] or 0
