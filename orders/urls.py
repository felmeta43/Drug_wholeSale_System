from django.urls import path
from . import views

urlpatterns = [
    path('purchase/', views.PurchaseOrderListView.as_view(), name='purchase_order_list'),
    path('purchase/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchase_order_detail'),
    path('purchase/<int:pk>/status/', views.purchase_order_update_status, name='purchase_order_status'),
    path('purchase/<int:pk>/approve/', views.purchase_order_approve, name='purchase_order_approve'),
    path('purchase/<int:pk>/receive/', views.receive_purchase_order, name='receive_purchase_order'),
    path('sales/', views.SalesOrderListView.as_view(), name='sales_order_list'),
    path('sales/create/', views.sales_order_create, name='sales_order_create'),
    path('sales/<int:pk>/', views.SalesOrderDetailView.as_view(), name='sales_order_detail'),
    path('sales/<int:pk>/edit/', views.sales_order_edit, name='sales_order_edit'),
    path('sales/<int:pk>/status/', views.sales_order_update_status, name='sales_order_status'),
    path('sales/<int:pk>/invoice/', views.generate_invoice_from_order, name='generate_invoice'),
]
