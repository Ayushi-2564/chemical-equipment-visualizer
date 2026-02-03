# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/user/', views.current_user, name='current_user'),
    
    # Dataset operations
    path('datasets/', views.dataset_list, name='dataset_list'),
    path('datasets/upload/', views.upload_csv, name='upload_csv'),
    path('datasets/<int:pk>/', views.dataset_detail, name='dataset_detail'),
    path('datasets/<int:pk>/delete/', views.dataset_delete, name='dataset_delete'),
    path('datasets/<int:pk>/report/', views.generate_report, name='generate_report'),
]