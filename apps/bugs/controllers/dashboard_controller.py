from django.shortcuts import render
from apps.accounts.decorators import custom_login_required
from apps.bugs.services.project_service import ProjectService
from apps.bugs.repositories.project_repository import ProjectRepository
from apps.bugs.repositories.project_member_repository import ProjectMemberRepository
from apps.bugs.repositories.bug_repository import BugRepository
from apps.bugs.repositories.role_repository import RoleRepository

@custom_login_required
def dashboard(request):
    # Injection
    project_repo = ProjectRepository()
    project_member_repo = ProjectMemberRepository()
    bug_repo = BugRepository()
    role_repo = RoleRepository()
    project_service = ProjectService(project_repo, project_member_repo, bug_repo, role_repo)
    
    user_projects = project_service.get_dashboard_projects(request.logged_user)
    return render(request, 'bugs/dashboard.html', {'projects': user_projects})
