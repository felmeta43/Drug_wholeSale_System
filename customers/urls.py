from django.urls import path
from . import views

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer_list'),
    path('create/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('<int:customer_pk>/documents/add/', views.add_customer_document, name='add_customer_document'),
    path('documents/<int:pk>/delete/', views.delete_customer_document, name='delete_customer_document'),
]
