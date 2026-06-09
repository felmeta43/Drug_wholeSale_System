from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'supplier_type', 'tin_number', 'business_license_number',
                  'efda_license_number', 'contact_person', 'email', 'phone', 'alt_phone',
                  'country', 'city', 'address', 'website', 'payment_terms', 'credit_limit',
                  'bank_name', 'bank_account_number', 'notes', 'is_active']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('Basic Information',
                Row(Column('name', css_class='col-md-8'),
                    Column('supplier_type', css_class='col-md-4')),
                Row(Column('tin_number', css_class='col-md-4'),
                    Column('business_license_number', css_class='col-md-4'),
                    Column('efda_license_number', css_class='col-md-4')),
                Row(Column('contact_person', css_class='col-md-6'),
                    Column('website', css_class='col-md-6')),
            ),
            Fieldset('Contact Details',
                Row(Column('email', css_class='col-md-4'),
                    Column('phone', css_class='col-md-4'),
                    Column('alt_phone', css_class='col-md-4')),
                Row(Column('country', css_class='col-md-4'),
                    Column('city', css_class='col-md-4')),
                'address',
            ),
            Fieldset('Payment & Banking',
                Row(Column('payment_terms', css_class='col-md-4'),
                    Column('credit_limit', css_class='col-md-4')),
                Row(Column('bank_name', css_class='col-md-6'),
                    Column('bank_account_number', css_class='col-md-6')),
            ),
            'notes',
            'is_active',
            Submit('submit', 'Save Supplier', css_class='btn btn-primary'),
        )
