from .models import CompanySettings


def company(request):
    """Inject company settings into every template context."""
    return {'company': CompanySettings.get()}
