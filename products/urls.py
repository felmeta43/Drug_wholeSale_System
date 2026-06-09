from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('variants/', views.ProductVariantListView.as_view(), name='variant_list'),
    path('variants/create/', views.ProductVariantCreateView.as_view(), name='variant_create'),
    path('variants/<int:pk>/edit/', views.ProductVariantUpdateView.as_view(), name='variant_update'),
    path('medicines/', views.MedicineListView.as_view(), name='medicine_list'),
    path('medicines/create/', views.MedicineCreateView.as_view(), name='medicine_create'),
    path('medicines/<int:pk>/edit/', views.MedicineUpdateView.as_view(), name='medicine_update'),
    path('api/variant-price/<int:pk>/', views.variant_price_api, name='variant_price_api'),
    path('api/search/', views.product_search_api, name='product_search_api'),
]
