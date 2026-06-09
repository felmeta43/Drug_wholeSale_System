from django.contrib import admin
from .models import Category, Product, ProductVariant, Medicine


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['sku', 'strength', 'packaging', 'cost_price', 'selling_price', 'tax_category', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'unit_of_measure', 'is_controlled_substance',
                    'requires_cold_chain', 'is_active']
    list_filter = ['category', 'is_controlled_substance', 'requires_cold_chain', 'is_active']
    search_fields = ['name', 'brand', 'model_number', 'efda_registration_number']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'strength', 'packaging', 'cost_price', 'selling_price', 'is_active']
    list_filter = ['tax_category', 'is_active']
    search_fields = ['product__name', 'sku', 'barcode', 'strength']


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['generic_name', 'dosage_form', 'strength', 'prescription_required',
                    'is_narcotic', 'is_psychotropic']
    list_filter = ['dosage_form', 'prescription_required', 'is_narcotic', 'is_psychotropic',
                   'therapeutic_category']
    search_fields = ['generic_name', 'brand_name', 'ethiopian_drug_code', 'atc_code']
