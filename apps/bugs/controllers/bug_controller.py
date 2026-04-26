from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.decorators import custom_login_required
from apps.bugs.services.bug_service import BugService
from apps.bugs.repositories.bug_repository import BugRepository
from apps.bugs.repositories.project_repository import ProjectRepository
from apps.bugs.repositories.project_member_repository import ProjectMemberRepository
from apps.bugs.repositories.bug_activity_log_repository import BugActivityLogRepository
from apps.bugs.models import Project

def _get_bug_service():
    return BugService(
        BugRepository(),
        ProjectRepository(),
        ProjectMemberRepository(),
        BugActivityLogRepository()
    )

@custom_login_required
def bug_detail(request, bug_id):
    bug_service = _get_bug_service()
    bug, status, activity_logs = bug_service.get_bug_detail(bug_id, request.logged_user)
    
    if status == 'NOT_FOUND':
        from django.http import Http404
        raise Http404("Bug not found")
    elif status == 'FORBIDDEN':
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        root_cause = request.POST.get('root_cause', '')
        assignee_id = request.POST.get('assign_to')
        
        if new_status:
            bug_service.update_bug_status(bug, new_status, root_cause, request.logged_user)
        
        if assignee_id:
            bug_service.assign_bug(bug, assignee_id, request.logged_user)
            
        return redirect('bug_detail', bug_id=bug.id)

    # Get project members for assignment dropdown
    project_members = ProjectMemberRepository().get_all_by_project(bug.project)

    return render(request, 'bugs/bug_detail.html', {
        'bug': bug, 
        'activity_logs': activity_logs,
        'project_members': project_members
    })

@custom_login_required
def create_bug(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        bug_service = _get_bug_service()
        project_obj, status = bug_service.create_bug(
            project_id, 
            request.POST.get('title'),
            request.POST.get('description'),
            request.POST.get('type'),
            request.POST.get('priority'),
            request.logged_user
        )
        if status == 'NOT_FOUND':
            from django.http import Http404
            raise Http404("Project not found")
        elif status == 'FORBIDDEN':
            return render(request, '403.html', status=403)
        return redirect('project_detail', project_id=project_id)
        
    return render(request, 'bugs/create_bug.html', {'project': project})
