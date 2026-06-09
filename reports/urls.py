from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_report, name='reports_home'),
    path('sales/', views.sales_report, name='sales_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('customers/', views.customer_report, name='customer_report'),
    path('suppliers/', views.supplier_report, name='supplier_report'),
    path('financial/', views.financial_summary, name='financial_summary'),
    path('expiry/', views.expiry_report_page, name='expiry_report_page'),
]
