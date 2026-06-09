from django.contrib import admin
from .models import Invoice, Payment, CreditNote


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['payment_date', 'amount', 'payment_method', 'reference_number', 'received_by']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'invoice_date', 'due_date', 'total_amount',
                    'amount_paid', 'balance_due', 'payment_status']
    list_filter = ['payment_status', 'invoice_date']
    search_fields = ['invoice_number', 'customer__name']
    inlines = [PaymentInline]
    date_hierarchy = 'invoice_date'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'payment_date', 'amount', 'payment_method', 'reference_number', 'received_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['invoice__invoice_number', 'reference_number']


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ['credit_note_number', 'customer', 'invoice', 'date', 'amount', 'is_applied']
    list_filter = ['is_applied', 'date']
    search_fields = ['credit_note_number', 'customer__name']
