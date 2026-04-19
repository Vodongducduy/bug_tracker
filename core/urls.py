from django.contrib import admin
from django.urls import path, include
from apps.accounts.controllers.auth_controller import login_view, logout_view, register_view
from apps.bugs.controllers.dashboard_controller import dashboard

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard, name='dashboard'),
    path('bugs/', include('apps.bugs.urls')),
]
