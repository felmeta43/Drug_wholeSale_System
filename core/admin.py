from django.contrib import admin
from .models import CompanySettings


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identity', {'fields': ('name', 'short_name', 'tagline', 'logo', 'logo_icon')}),
        ('Contact', {'fields': ('address', 'city', 'country', 'phone', 'email', 'website')}),
        ('Legal & Tax', {'fields': ('tin_number', 'vat_number', 'business_license', 'regulatory_body', 'regulatory_license')}),
        ('Financial', {'fields': ('currency', 'currency_symbol', 'vat_rate', 'vat_label', 'withholding_tax_rate', 'enable_vat')}),
        ('Document Numbering', {'fields': ('invoice_prefix', 'po_prefix', 'so_prefix', 'credit_note_prefix')}),
        ('Document Defaults', {'fields': ('invoice_footer', 'invoice_terms', 'default_payment_terms_days', 'expiry_alert_days')}),
        ('Branding', {'fields': ('primary_color', 'secondary_color', 'accent_color', 'sidebar_dark')}),
        ('Localisation', {'fields': ('timezone', 'date_format', 'language_code')}),
        ('Features', {'fields': ('enable_cold_chain', 'enable_controlled_substances', 'enable_batch_tracking', 'enable_multi_warehouse')}),
    )

    def has_add_permission(self, request):
        return not CompanySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
