from django.urls import path
from . import views

urlpatterns = [
    path('', views.InvoiceListView.as_view(), name='invoice_list'),
    path('create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('<int:invoice_pk>/payment/', views.record_payment, name='record_payment'),
    path('<int:pk>/print/', views.invoice_print, name='invoice_print'),
    path('credit-notes/', views.CreditNoteListView.as_view(), name='credit_note_list'),
    path('credit-notes/create/', views.CreditNoteCreateView.as_view(), name='credit_note_create'),
    path('aged-receivables/', views.aged_receivables, name='aged_receivables'),
]
