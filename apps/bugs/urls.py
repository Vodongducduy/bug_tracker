from django.urls import path
from apps.bugs.controllers.dashboard_controller import dashboard
from apps.bugs.controllers.project_controller import project_detail, create_project
from apps.bugs.controllers.bug_controller import bug_detail, create_bug
from apps.bugs.controllers.member_controller import manage_members, remove_member

urlpatterns = [
    path('project/<int:project_id>/', project_detail, name='project_detail'),
    path('project/create/', create_project, name='create_project'),
    path('project/<int:project_id>/members/', manage_members, name='manage_members'),
    path('project/<int:project_id>/members/remove/<int:user_id>/', remove_member, name='remove_member'),
    path('project/<int:project_id>/create/', create_bug, name='create_bug'),
    path('<int:bug_id>/', bug_detail, name='bug_detail'),
]
