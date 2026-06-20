from django.urls import path
from . import views

urlpatterns = [
    path('', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('create/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse_detail'),
    path('<int:pk>/edit/', views.WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('transfers/', views.StockTransferListView.as_view(), name='transfer_list'),
    path('transfers/create/', views.stock_transfer_create, name='transfer_create'),
    path('transfers/request/', views.stock_transfer_request_create, name='transfer_request_create'),
    path('transfers/<int:pk>/', views.StockTransferDetailView.as_view(), name='transfer_detail'),
    path('transfers/<int:pk>/approve-request/', views.stock_transfer_approve_request, name='transfer_approve_request'),
    path('transfers/<int:pk>/complete/', views.complete_transfer, name='complete_transfer'),
]
