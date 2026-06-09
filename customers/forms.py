from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import Customer, CustomerDocument


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'customer_type', 'tin_number', 'business_license_number',
                  'license_expiry_date', 'efda_license_number', 'contact_person',
                  'email', 'phone', 'alt_phone', 'region', 'zone', 'woreda',
                  'kebele', 'city', 'address', 'credit_limit', 'credit_days',
                  'discount_percentage', 'notes', 'is_active']
        widgets = {
            'license_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('Basic Information',
                Row(Column('name', css_class='col-md-8'),
                    Column('customer_type', css_class='col-md-4')),
                Row(Column('tin_number', css_class='col-md-4'),
                    Column('business_license_number', css_class='col-md-4'),
                    Column('license_expiry_date', css_class='col-md-4')),
                Row(Column('efda_license_number', css_class='col-md-6'),
                    Column('contact_person', css_class='col-md-6')),
            ),
            Fieldset('Contact Details',
                Row(Column('email', css_class='col-md-4'),
                    Column('phone', css_class='col-md-4'),
                    Column('alt_phone', css_class='col-md-4')),
            ),
            Fieldset('Location',
                Row(Column('region', css_class='col-md-4'),
                    Column('zone', css_class='col-md-4'),
                    Column('woreda', css_class='col-md-4')),
                Row(Column('kebele', css_class='col-md-4'),
                    Column('city', css_class='col-md-4')),
                'address',
            ),
            Fieldset('Credit & Financial',
                Row(Column('credit_limit', css_class='col-md-4'),
                    Column('credit_days', css_class='col-md-4'),
                    Column('discount_percentage', css_class='col-md-4')),
            ),
            'notes',
            'is_active',
            Submit('submit', 'Save Customer', css_class='btn btn-primary'),
        )


class CustomerDocumentForm(forms.ModelForm):
    class Meta:
        model = CustomerDocument
        fields = ['document_type', 'file', 'description', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
