from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CompanySettings
from .forms import CompanySettingsForm


@login_required
def company_settings(request):
    if not (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'):
        messages.error(request, 'You do not have permission to access company settings.')
        return redirect('dashboard')

    obj = CompanySettings.get()
    form = CompanySettingsForm(request.POST or None, request.FILES or None, instance=obj)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Company settings saved successfully.')
        return redirect('company_settings')

    return render(request, 'core/settings.html', {
        'form': form,
        'company': obj,
        'title': 'Company Settings',
    })


@login_required
def settings_preview(request):
    """Return company branding as JSON for live preview."""
    company = CompanySettings.get()
    return JsonResponse({
        'name': company.name,
        'short_name': company.short_name,
        'primary_color': company.primary_color,
        'secondary_color': company.secondary_color,
        'accent_color': company.accent_color,
        'currency_symbol': company.currency_symbol,
        'vat_rate': str(company.vat_rate),
    })
