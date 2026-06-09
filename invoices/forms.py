from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Invoice, Payment, CreditNote


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'sales_order', 'invoice_date', 'due_date',
                  'subtotal', 'discount_amount', 'vat_amount', 'total_amount', 'notes']
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('customer', css_class='col-md-6'),
                Column('sales_order', css_class='col-md-6')),
            Row(Column('invoice_date', css_class='col-md-6'),
                Column('due_date', css_class='col-md-6')),
            Row(Column('subtotal', css_class='col-md-3'),
                Column('discount_amount', css_class='col-md-3'),
                Column('vat_amount', css_class='col-md-3'),
                Column('total_amount', css_class='col-md-3')),
            'notes',
            Submit('submit', 'Save Invoice', css_class='btn btn-primary'),
        )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['invoice', 'payment_date', 'amount', 'payment_method',
                  'reference_number', 'bank_name', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('invoice', css_class='col-md-6'),
                Column('payment_date', css_class='col-md-6')),
            Row(Column('amount', css_class='col-md-4'),
                Column('payment_method', css_class='col-md-4'),
                Column('reference_number', css_class='col-md-4')),
            Row(Column('bank_name', css_class='col-md-6')),
            'notes',
            Submit('submit', 'Record Payment', css_class='btn btn-success'),
        )


class CreditNoteForm(forms.ModelForm):
    class Meta:
        model = CreditNote
        fields = ['invoice', 'customer', 'date', 'reason', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('invoice', css_class='col-md-6'),
                Column('customer', css_class='col-md-6')),
            Row(Column('date', css_class='col-md-4'),
                Column('amount', css_class='col-md-4')),
            'reason',
            Submit('submit', 'Create Credit Note', css_class='btn btn-warning'),
        )
