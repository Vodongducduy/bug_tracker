from django.shortcuts import render, redirect
from apps.accounts.decorators import custom_login_required
from apps.bugs.services.project_service import ProjectService
from apps.bugs.repositories.project_repository import ProjectRepository
from apps.bugs.repositories.project_member_repository import ProjectMemberRepository
from apps.bugs.repositories.bug_repository import BugRepository
from apps.bugs.repositories.role_repository import RoleRepository

def _get_project_service():
    return ProjectService(
        ProjectRepository(),
        ProjectMemberRepository(),
        BugRepository(),
        RoleRepository()
    )

@custom_login_required
def project_detail(request, project_id):
    project_service = _get_project_service()
    project, status, bugs = project_service.get_project_detail(project_id, request.logged_user)
    
    if not project:
        from django.http import Http404
        raise Http404("Project not found")
        
    if status == 'FORBIDDEN':
        return render(request, '403.html', status=403)
        
    user_role = status if status != 'OK' and status != 'FORBIDDEN' else None 
    if status != 'FORBIDDEN':
        user_role = status 

    return render(request, 'bugs/project_detail.html', {
        'project': project, 
        'bugs': bugs,
        'user_role': user_role
    })

@custom_login_required
def create_project(request):
    if not request.logged_user.is_superuser:
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        project_service = _get_project_service()
        project = project_service.create_project(
            request.POST.get('name'), 
            request.POST.get('description'), 
            request.logged_user
        )
        if project:
            return redirect('dashboard')
                
    return render(request, 'bugs/create_project.html')
