from django.contrib import admin
from django.urls import path, include
from apps.accounts.controllers.auth_controller import login_view, logout_view, register_view
from apps.accounts.controllers.account_controller import account_list, create_account, toggle_status
from apps.bugs.controllers.dashboard_controller import dashboard

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('accounts/', account_list, name='account_list'),
    path('accounts/create/', create_account, name='admin_create_account'),
    path('accounts/toggle/<int:user_id>/', toggle_status, name='admin_toggle_status'),
    path('', dashboard, name='dashboard'),
    path('bugs/', include('apps.bugs.urls')),
]
