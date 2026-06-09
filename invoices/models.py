from django.db import models
from django.conf import settings
import datetime


class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    sales_order = models.OneToOneField('orders.SalesOrder', on_delete=models.PROTECT,
                                        related_name='invoice', null=True, blank=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='invoices')
    invoice_date = models.DateField(default=datetime.date.today)
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name='invoices_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from core.models import CompanySettings
            prefix = CompanySettings.get().invoice_prefix
            last = Invoice.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.invoice_number = f"{prefix}{datetime.date.today().strftime('%Y%m')}-{num:04d}"
        self.balance_due = self.total_amount - self.amount_paid
        if self.balance_due <= 0:
            self.payment_status = 'paid'
        elif self.amount_paid > 0:
            self.payment_status = 'partial'
        super().save(*args, **kwargs)

    def update_payment_status(self):
        self.amount_paid = sum(p.amount for p in self.payments.all())
        self.balance_due = self.total_amount - self.amount_paid
        if self.balance_due <= 0:
            self.payment_status = 'paid'
        elif self.amount_paid > 0:
            self.payment_status = 'partial'
        else:
            from django.utils import timezone
            if self.due_date < timezone.now().date():
                self.payment_status = 'overdue'
        self.save()

    def is_overdue(self):
        from django.utils import timezone
        return self.payment_status != 'paid' and self.due_date < timezone.now().date()


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('mobile_money', 'Mobile Money'),
        ('credit', 'Credit'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    payment_date = models.DateField(default=datetime.date.today)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_number = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                     related_name='payments_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment for {self.invoice.invoice_number} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.update_payment_status()


class CreditNote(models.Model):
    credit_note_number = models.CharField(max_length=50, unique=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='credit_notes')
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='credit_notes')
    date = models.DateField(default=datetime.date.today)
    reason = models.TextField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    is_applied = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name='credit_notes_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Credit Note'
        verbose_name_plural = 'Credit Notes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.credit_note_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.credit_note_number:
            from core.models import CompanySettings
            prefix = CompanySettings.get().credit_note_prefix
            last = CreditNote.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.credit_note_number = f"{prefix}{datetime.date.today().strftime('%Y%m')}-{num:04d}"
        super().save(*args, **kwargs)
