from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_in, name='sign_in'),  # Default route to Sign-in page
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory, name='inventory'),
    path('bills/', views.bills, name='bills'),
    path('admin-page/', views.admin_page, name='admin_page'),
]