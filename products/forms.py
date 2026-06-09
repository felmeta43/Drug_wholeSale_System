from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import Category, Product, ProductVariant, Medicine


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'image', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('name', css_class='col-md-8'), Column('is_active', css_class='col-md-4')),
            'description',
            Row(Column('parent', css_class='col-md-6'), Column('image', css_class='col-md-6')),
            Submit('submit', 'Save Category', css_class='btn btn-primary'),
        )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'model_number', 'description',
                  'unit_of_measure', 'efda_registration_number', 'is_controlled_substance',
                  'requires_cold_chain', 'reorder_level', 'weight', 'image', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('name', css_class='col-md-8'), Column('category', css_class='col-md-4')),
            Row(Column('brand', css_class='col-md-6'), Column('model_number', css_class='col-md-6')),
            'description',
            Row(Column('unit_of_measure', css_class='col-md-4'),
                Column('efda_registration_number', css_class='col-md-4'),
                Column('reorder_level', css_class='col-md-4')),
            Row(Column('weight', css_class='col-md-4'),
                Column('image', css_class='col-md-4')),
            Row(Column('is_controlled_substance', css_class='col-md-4'),
                Column('requires_cold_chain', css_class='col-md-4'),
                Column('is_active', css_class='col-md-4')),
            Submit('submit', 'Save Product', css_class='btn btn-primary'),
        )


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['product', 'sku', 'barcode', 'size', 'packaging', 'strength',
                  'cost_price', 'selling_price', 'min_selling_price', 'tax_category', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('product', css_class='col-md-8'), Column('sku', css_class='col-md-4')),
            Row(Column('barcode', css_class='col-md-4'),
                Column('strength', css_class='col-md-4'),
                Column('packaging', css_class='col-md-4')),
            Row(Column('size', css_class='col-md-4')),
            Row(Column('cost_price', css_class='col-md-4'),
                Column('selling_price', css_class='col-md-4'),
                Column('min_selling_price', css_class='col-md-4')),
            Row(Column('tax_category', css_class='col-md-6'), Column('is_active', css_class='col-md-6')),
            Submit('submit', 'Save Variant', css_class='btn btn-primary'),
        )


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['product', 'generic_name', 'brand_name', 'dosage_form', 'strength',
                  'route_of_administration', 'therapeutic_category', 'pharmacological_class',
                  'prescription_required', 'is_narcotic', 'is_psychotropic',
                  'storage_condition', 'shelf_life_months', 'ethiopian_drug_code',
                  'atc_code', 'manufacturer', 'country_of_origin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('product', css_class='col-md-12')),
            Row(Column('generic_name', css_class='col-md-6'), Column('brand_name', css_class='col-md-6')),
            Row(Column('dosage_form', css_class='col-md-4'),
                Column('strength', css_class='col-md-4'),
                Column('route_of_administration', css_class='col-md-4')),
            Row(Column('therapeutic_category', css_class='col-md-6'),
                Column('pharmacological_class', css_class='col-md-6')),
            Row(Column('storage_condition', css_class='col-md-4'),
                Column('shelf_life_months', css_class='col-md-4'),
                Column('atc_code', css_class='col-md-4')),
            Row(Column('ethiopian_drug_code', css_class='col-md-6'),
                Column('manufacturer', css_class='col-md-6')),
            Row(Column('country_of_origin', css_class='col-md-4')),
            Row(Column('prescription_required', css_class='col-md-4'),
                Column('is_narcotic', css_class='col-md-4'),
                Column('is_psychotropic', css_class='col-md-4')),
            Submit('submit', 'Save Medicine Info', css_class='btn btn-primary'),
        )
