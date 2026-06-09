from django.contrib import admin
from .models import Customer, CustomerDocument


class CustomerDocumentInline(admin.TabularInline):
    model = CustomerDocument
    extra = 0
    fields = ['document_type', 'file', 'expiry_date', 'description']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer_type', 'phone', 'region', 'credit_limit', 'is_active']
    list_filter = ['customer_type', 'region', 'is_active']
    search_fields = ['name', 'tin_number', 'phone', 'email', 'contact_person']
    inlines = [CustomerDocumentInline]


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'document_type', 'expiry_date', 'uploaded_at']
    list_filter = ['document_type']
    search_fields = ['customer__name']
