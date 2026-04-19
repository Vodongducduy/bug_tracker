from django.shortcuts import render, redirect
from apps.accounts.decorators import custom_login_required
from apps.bugs.services.member_service import ProjectMemberService
from apps.bugs.repositories.project_repository import ProjectRepository
from apps.bugs.repositories.project_member_repository import ProjectMemberRepository
from apps.bugs.repositories.user_repository import UserRepository
from apps.bugs.repositories.role_repository import RoleRepository

def _get_project_member_service():
    return ProjectMemberService(
        ProjectRepository(),
        ProjectMemberRepository(),
        UserRepository(),
        RoleRepository()
    )

@custom_login_required
def manage_members(request, project_id):
    project_member_service = _get_project_member_service()
    if request.method == 'POST':
        project, status = project_member_service.manage_member(
            project_id,
            request.POST.get('user_id'),
            request.POST.get('role_id'),
            request.logged_user
        )
        if status == 'FORBIDDEN':
            return render(request, '403.html', status=403)
        elif status == 'NOT_FOUND':
            from django.http import Http404
            raise Http404("Project/User/Role not found")
            
        return redirect('manage_members', project_id=project_id)

    context, status = project_member_service.get_manage_members_context(project_id, request.logged_user)
    if status == 'FORBIDDEN':
        return render(request, '403.html', status=403)
    elif status == 'NOT_FOUND':
        from django.http import Http404
        raise Http404("Project not found")
        
    return render(request, 'bugs/manage_members.html', context)

@custom_login_required
def remove_member(request, project_id, user_id):
    project_member_service = _get_project_member_service()
    project, status = project_member_service.remove_member(project_id, user_id, request.logged_user)
    
    if status == 'FORBIDDEN':
        return render(request, '403.html', status=403)
    elif status == 'NOT_FOUND':
        from django.http import Http404
        raise Http404("Not found")
        
    return redirect('manage_members', project_id=project_id)
