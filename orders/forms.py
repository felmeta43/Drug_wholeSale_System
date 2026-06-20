from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'warehouse', 'order_date', 'expected_delivery_date', 'notes']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('supplier', css_class='col-md-6'),
                Column('warehouse', css_class='col-md-6')),
            Row(Column('order_date', css_class='col-md-6'),
                Column('expected_delivery_date', css_class='col-md-6')),
            'notes',
            Submit('submit', 'Save Purchase Order', css_class='btn btn-primary'),
        )


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['product_variant', 'quantity', 'unit_price', 'discount_percent',
                  'batch_number', 'expiry_date']
        widgets = {
            'product_variant': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'max': '100'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Batch #'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
        }


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=3, can_delete=True
)


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'warehouse', 'order_date', 'delivery_date',
                  'payment_terms', 'discount_amount', 'notes']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('customer', css_class='col-md-6'),
                Column('warehouse', css_class='col-md-6')),
            Row(Column('order_date', css_class='col-md-4'),
                Column('delivery_date', css_class='col-md-4'),
                Column('payment_terms', css_class='col-md-4')),
            Row(Column('discount_amount', css_class='col-md-4')),
            'notes',
            Submit('submit', 'Save Sales Order', css_class='btn btn-primary'),
        )


class SalesOrderItemForm(forms.ModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ['product_variant', 'batch', 'quantity', 'unit_price', 'discount_percent']
        widgets = {
            'product_variant': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'readonly': 'readonly'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


SalesOrderItemFormSet = inlineformset_factory(
    SalesOrder, SalesOrderItem,
    form=SalesOrderItemForm,
    extra=3, can_delete=True
)
