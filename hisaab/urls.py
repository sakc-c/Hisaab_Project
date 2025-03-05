from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),  # Default route to Sign-in page
    path('/logout', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory, name='inventory'),
    path('bills/', views.bills, name='bills'),
    path('reports/', views.reports, name='reports'),
    path('user_management/', views.user_management, name='user_management'),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<int:category_id>/', views.category_detail, name='category'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
]
