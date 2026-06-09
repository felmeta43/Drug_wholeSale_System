from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import Warehouse, StockTransfer, StockTransferItem


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'code', 'address', 'city', 'region', 'manager',
                  'phone', 'email', 'has_cold_storage', 'cold_storage_capacity', 'notes', 'is_active']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('name', css_class='col-md-8'),
                Column('code', css_class='col-md-4')),
            Row(Column('manager', css_class='col-md-6'),
                Column('phone', css_class='col-md-3'),
                Column('email', css_class='col-md-3')),
            Row(Column('city', css_class='col-md-4'),
                Column('region', css_class='col-md-4')),
            'address',
            Row(Column('has_cold_storage', css_class='col-md-4'),
                Column('cold_storage_capacity', css_class='col-md-4')),
            'notes',
            'is_active',
            Submit('submit', 'Save Warehouse', css_class='btn btn-primary'),
        )


class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['from_warehouse', 'to_warehouse', 'transfer_date', 'notes']
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('from_warehouse', css_class='col-md-6'),
                Column('to_warehouse', css_class='col-md-6')),
            Row(Column('transfer_date', css_class='col-md-4')),
            'notes',
            Submit('submit', 'Create Transfer', css_class='btn btn-primary'),
        )


class StockTransferItemForm(forms.ModelForm):
    class Meta:
        model = StockTransferItem
        fields = ['product_variant', 'batch', 'quantity_sent', 'notes']


StockTransferItemFormSet = inlineformset_factory(
    StockTransfer, StockTransferItem,
    form=StockTransferItemForm,
    extra=3, can_delete=True
)
