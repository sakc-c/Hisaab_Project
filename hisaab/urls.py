
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.urls import path

from hisaab_project import settings

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('profile'), template_name='hisaab/reset_password.html',), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('inventory/', views.inventory, name='inventory'),
    path('bills/', views.bills, name='bills'),
    path('reports/', views.reports, name='reports'),
    path('user_management/', views.user_management, name='user_management'),
    path('create-user/', views.create_user, name='create_user'),
    path('change-password/<int:user_id>/', views.change_password, name='change_password'),
    # path('delete-user/<int:user_id>/', views.delete_user_page, name='delete_user_page'),
    # path('delete-user-action/<int:user_id>/', views.delete_user, name='delete_user_action'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<int:category_id>/', views.category_detail, name='category'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('bills/', views.bills, name='bills'),
    path('bills/delete/<int:bill_id>/', views.delete_bill, name='delete_bill'),
    path('bills/create_bill/', views.create_bill, name='create_bill'),
    path('bills/download_pdf/<int:bill_id>/', views.download_pdf, name='download_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
