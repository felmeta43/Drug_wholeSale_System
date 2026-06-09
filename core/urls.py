from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.company_settings, name='company_settings'),
    path('settings/preview/', views.settings_preview, name='settings_preview'),
]
