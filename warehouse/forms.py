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


# ── Request Transfer workflow (initiated by the RECEIVING warehouse) ──────────

class StockTransferRequestForm(StockTransferForm):
    """Same fields as StockTransferForm; receiver fills this in to request stock."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Row(Column('from_warehouse', css_class='col-md-6'),
                Column('to_warehouse', css_class='col-md-6')),
            Row(Column('transfer_date', css_class='col-md-4')),
            'notes',
            Submit('submit', 'Submit Request', css_class='btn btn-primary'),
        )


class StockTransferRequestItemForm(forms.ModelForm):
    class Meta:
        model = StockTransferItem
        fields = ['product_variant', 'quantity_requested', 'notes']


StockTransferRequestItemFormSet = inlineformset_factory(
    StockTransfer, StockTransferItem,
    form=StockTransferRequestItemForm,
    fields=['product_variant', 'quantity_requested', 'notes'],
    extra=3, can_delete=True
)


class StockTransferApproveItemForm(forms.ModelForm):
    class Meta:
        model = StockTransferItem
        fields = ['batch', 'quantity_sent']

    def __init__(self, *args, from_warehouse=None, **kwargs):
        super().__init__(*args, **kwargs)
        from inventory.models import StockBatch
        if product_variant_id := getattr(self.instance, 'product_variant_id', None):
            qs = StockBatch.objects.filter(
                product_variant_id=product_variant_id,
                quantity_available__gt=0
            )
            if from_warehouse is not None:
                qs = qs.filter(warehouse=from_warehouse)
            self.fields['batch'].queryset = qs
        else:
            self.fields['batch'].queryset = StockBatch.objects.none()


StockTransferApproveItemFormSet = inlineformset_factory(
    StockTransfer, StockTransferItem,
    form=StockTransferApproveItemForm,
    fields=['batch', 'quantity_sent'],
    extra=0, can_delete=False
)


class StockTransferReceiveItemForm(forms.ModelForm):
    class Meta:
        model = StockTransferItem
        fields = ['quantity_received']
        widgets = {
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'style': 'width:100px;', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.quantity_received and self.instance.quantity_sent:
            self.initial['quantity_received'] = self.instance.quantity_sent
        if self.instance.quantity_sent:
            self.fields['quantity_received'].widget.attrs['max'] = self.instance.quantity_sent

    def has_changed(self):
        # extra=0 formset bound to real existing items: always process the
        # row on submit, even if the prefilled initial matches what was
        # submitted (e.g. receiver accepts the suggested full quantity as-is).
        return True


StockTransferReceiveItemFormSet = inlineformset_factory(
    StockTransfer, StockTransferItem,
    form=StockTransferReceiveItemForm,
    fields=['quantity_received'],
    extra=0, can_delete=False
)
