from django.urls import path
from . import views

urlpatterns = [
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/members/', views.manage_members, name='manage_members'),
    path('project/<int:project_id>/members/remove/<int:user_id>/', views.remove_member, name='remove_member'),
    path('project/<int:project_id>/create/', views.create_bug, name='create_bug'),
    path('<int:bug_id>/', views.bug_detail, name='bug_detail'),
]
