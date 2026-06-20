from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/read/', views.mark_read, name='notification_read'),
    path('mark-all-read/', views.mark_all_read, name='notification_mark_all_read'),
]
