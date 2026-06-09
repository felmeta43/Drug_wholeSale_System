from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import StockBatch, StockMovement, StockAlert


class StockBatchForm(forms.ModelForm):
    class Meta:
        model = StockBatch
        fields = ['product_variant', 'warehouse', 'batch_number', 'lot_number',
                  'manufacture_date', 'expiry_date', 'quantity_received', 'quantity_available',
                  'purchase_price', 'supplier']
        widgets = {
            'manufacture_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('product_variant', css_class='col-md-6'),
                Column('warehouse', css_class='col-md-6')),
            Row(Column('batch_number', css_class='col-md-4'),
                Column('lot_number', css_class='col-md-4'),
                Column('supplier', css_class='col-md-4')),
            Row(Column('manufacture_date', css_class='col-md-4'),
                Column('expiry_date', css_class='col-md-4'),
                Column('purchase_price', css_class='col-md-4')),
            Row(Column('quantity_received', css_class='col-md-6'),
                Column('quantity_available', css_class='col-md-6')),
            Submit('submit', 'Save Batch', css_class='btn btn-primary'),
        )


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['batch', 'movement_type', 'from_warehouse', 'to_warehouse',
                  'quantity', 'unit_price', 'reference_number', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('batch', css_class='col-md-6'),
                Column('movement_type', css_class='col-md-6')),
            Row(Column('from_warehouse', css_class='col-md-6'),
                Column('to_warehouse', css_class='col-md-6')),
            Row(Column('quantity', css_class='col-md-4'),
                Column('unit_price', css_class='col-md-4'),
                Column('reference_number', css_class='col-md-4')),
            'reason',
            Submit('submit', 'Record Movement', css_class='btn btn-primary'),
        )


class StockAdjustmentForm(forms.Form):
    batch = forms.ModelChoiceField(queryset=StockBatch.objects.all(), label='Stock Batch')
    adjustment_type = forms.ChoiceField(choices=[('add', 'Add Stock'), ('remove', 'Remove Stock')])
    quantity = forms.IntegerField(min_value=1)
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    reference_number = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('batch', css_class='col-md-6'),
                Column('adjustment_type', css_class='col-md-3'),
                Column('quantity', css_class='col-md-3')),
            Row(Column('reference_number', css_class='col-md-6')),
            'reason',
            Submit('submit', 'Apply Adjustment', css_class='btn btn-warning'),
        )
