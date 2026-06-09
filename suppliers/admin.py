from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier_type', 'country', 'phone', 'payment_terms', 'is_active']
    list_filter = ['supplier_type', 'country', 'is_active']
    search_fields = ['name', 'tin_number', 'phone', 'email', 'contact_person']
