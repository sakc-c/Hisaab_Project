from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),  # Default route to Sign-in page
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory, name='inventory'),
    path('bills/', views.bills, name='bills'),
    path('reports/', views.reports, name='reports'),
    path('user_management/', views.user_management, name='user_management'),
    path('create-user/', views.create_user, name='create_user'),
    path('change-password/<int:user_id>/', views.change_password, name='change_password'),
    path('delete-user/<int:user_id>/', views.delete_user_page, name='delete_user_page'),
    path('delete-user-action/<int:user_id>/', views.delete_user, name='delete_user_action'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_product/',views.add_product, name='add_product'),
    path('category/<int:category_id>/', views.category_detail, name='category'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
]
