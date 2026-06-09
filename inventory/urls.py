from django.urls import path
from . import views

urlpatterns = [
    path('', views.StockOverviewView.as_view(), name='stock_overview'),
    path('batches/create/', views.StockBatchCreateView.as_view(), name='batch_create'),
    path('batches/<int:pk>/', views.StockBatchDetailView.as_view(), name='batch_detail'),
    path('batches/<int:pk>/edit/', views.StockBatchUpdateView.as_view(), name='batch_update'),
    path('movements/', views.StockMovementListView.as_view(), name='movement_list'),
    path('adjustment/', views.stock_adjustment, name='stock_adjustment'),
    path('alerts/', views.AlertListView.as_view(), name='alert_list'),
    path('alerts/<int:pk>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('expiry-report/', views.expiry_report, name='expiry_report'),
]
