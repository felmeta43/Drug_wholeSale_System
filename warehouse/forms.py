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
        widgets = {
            'product_variant': forms.Select(attrs={'class': 'form-select form-select-sm js-variant-select'}),
            'batch': forms.Select(attrs={'class': 'form-select form-select-sm js-batch-select'}),
            'quantity_sent': forms.NumberInput(attrs={'class': 'form-control form-control-sm js-qty-input', 'min': '1'}),
            'notes': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from inventory.models import StockBatch
        # The front-end populates this select via AJAX scoped to the chosen
        # source warehouse/product, so the queryset here only needs to allow
        # any in-stock batch through model validation — it can't be narrowed
        # to a single warehouse upfront since no warehouse is known until the
        # user picks one client-side.
        self.fields['batch'].queryset = StockBatch.objects.filter(quantity_available__gt=0)

    def clean(self):
        cleaned_data = super().clean()
        batch = cleaned_data.get('batch')
        quantity_sent = cleaned_data.get('quantity_sent')
        if batch and quantity_sent and quantity_sent > batch.quantity_available:
            raise forms.ValidationError(
                f'Cannot send {quantity_sent} — only {batch.quantity_available} available in batch {batch.batch_number}.'
            )
        return cleaned_data


StockTransferItemFormSet = inlineformset_factory(
    StockTransfer, StockTransferItem,
    form=StockTransferItemForm,
    extra=1, can_delete=True
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
        widgets = {
            'product_variant': forms.Select(attrs={'class': 'form-select form-select-sm js-variant-select'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control form-control-sm js-qty-input', 'min': '1'}),
            'notes': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }


StockTransferRequestItemFormSet = inlineformset_factory(
    StockTransfer, StockTransferItem,
    form=StockTransferRequestItemForm,
    fields=['product_variant', 'quantity_requested', 'notes'],
    extra=1, can_delete=True
)


class BatchSelectWithStock(forms.Select):
    """Renders each batch <option> with a data-available attribute so the
    front-end can validate quantity_sent against real stock without an
    extra round-trip."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            from inventory.models import StockBatch
            pk = value.value if hasattr(value, 'value') else value
            available = StockBatch.objects.filter(pk=pk).values_list('quantity_available', flat=True).first()
            if available is not None:
                option['attrs']['data-available'] = available
        return option


class StockTransferApproveItemForm(forms.ModelForm):
    class Meta:
        model = StockTransferItem
        fields = ['batch', 'quantity_sent']
        widgets = {
            'batch': BatchSelectWithStock(attrs={'class': 'form-select form-select-sm js-batch-select'}),
            'quantity_sent': forms.NumberInput(attrs={'class': 'form-control form-control-sm js-qty-input', 'min': '1'}),
        }

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
        self.fields['quantity_sent'].widget.attrs['data-requested'] = self.instance.quantity_requested or ''


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
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control form-control-sm js-qty-input', 'style': 'width:100px;', 'min': 0}),
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
