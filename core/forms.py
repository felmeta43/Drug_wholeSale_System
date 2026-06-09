from django import forms
from .models import CompanySettings


class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        exclude = ['updated_at']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'invoice_footer': forms.Textarea(attrs={'rows': 3}),
            'invoice_terms': forms.Textarea(attrs={'rows': 4}),
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.TextInput)) or \
               'type' not in field.widget.attrs:
                if not isinstance(field.widget, (forms.CheckboxInput,)):
                    field.widget.attrs.setdefault('class', 'form-control')
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
