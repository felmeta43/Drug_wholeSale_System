from django.db import models


ETHIOPIAN_REGIONS = [
    ('addis_ababa', 'Addis Ababa'),
    ('afar', 'Afar'),
    ('amhara', 'Amhara'),
    ('benishangul_gumuz', 'Benishangul-Gumuz'),
    ('dire_dawa', 'Dire Dawa'),
    ('gambela', 'Gambela'),
    ('harari', 'Harari'),
    ('oromia', 'Oromia'),
    ('sidama', 'Sidama'),
    ('snnpr', 'SNNPR'),
    ('somali', 'Somali'),
    ('tigray', 'Tigray'),
    ('sw_ethiopia', 'South West Ethiopia'),
]


class Customer(models.Model):
    CUSTOMER_TYPES = [
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('pharmacy', 'Pharmacy'),
        ('health_center', 'Health Center'),
        ('drug_store', 'Drug Store'),
        ('ngo', 'NGO / Non-Profit'),
        ('government', 'Government Facility'),
        ('private', 'Private Individual'),
    ]

    name = models.CharField(max_length=300)
    customer_type = models.CharField(max_length=30, choices=CUSTOMER_TYPES, default='pharmacy')
    tin_number = models.CharField(max_length=50, blank=True, verbose_name='TIN Number')
    business_license_number = models.CharField(max_length=100, blank=True)
    license_expiry_date = models.DateField(null=True, blank=True)
    efda_license_number = models.CharField(max_length=100, blank=True, verbose_name='EFDA License Number')
    contact_person = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    alt_phone = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=30, choices=ETHIOPIAN_REGIONS, blank=True)
    zone = models.CharField(max_length=100, blank=True)
    woreda = models.CharField(max_length=100, blank=True)
    kebele = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit_days = models.PositiveIntegerField(default=30, help_text='Number of days for credit payment')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_customer_type_display()})"

    def get_outstanding_balance(self):
        from invoices.models import Invoice
        from django.db.models import Sum
        result = Invoice.objects.filter(
            customer=self,
            payment_status__in=['unpaid', 'partial', 'overdue']
        ).aggregate(total=Sum('balance_due'))
        return result['total'] or 0

    def get_total_orders(self):
        return self.sales_orders.count()


class CustomerDocument(models.Model):
    DOCUMENT_TYPES = [
        ('business_license', 'Business License'),
        ('efda_license', 'EFDA License'),
        ('tin_certificate', 'TIN Certificate'),
        ('drug_retail_license', 'Drug Retail License'),
        ('other', 'Other'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='customer_documents/')
    description = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Customer Document'
        verbose_name_plural = 'Customer Documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.customer.name} - {self.get_document_type_display()}"
