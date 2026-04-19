from django.shortcuts import render, get_object_or_404, redirect
from apps.accounts.decorators import custom_login_required
from .models import Project, Bug, BugActivityLog, ProjectMember
from apps.accounts.models import Role, User
from django.db import transaction

from django.db.models import Count, Q

@custom_login_required
def dashboard(request):
    # Get projects where the user is a member
    user_projects = Project.objects.filter(members__user=request.logged_user)
    return render(request, 'bugs/dashboard.html', {'projects': user_projects})

@custom_login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Check if user is member
    membership = ProjectMember.objects.filter(project=project, user=request.logged_user).select_related('role').first()
    if not membership and not request.logged_user.is_superuser:
        return render(request, '403.html', status=403)
        
    user_role = membership.role.title if membership else None
    
    bugs = project.bugs.all().order_by('-updated_at')
    return render(request, 'bugs/project_detail.html', {
        'project': project, 
        'bugs': bugs,
        'user_role': user_role
    })

@custom_login_required
def bug_detail(request, bug_id):
    bug = get_object_or_404(Bug, id=bug_id)
    # Check project membership
    if not ProjectMember.objects.filter(project=bug.project, user=request.logged_user).exists():
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        # Simple status update logic
        new_status = request.POST.get('status')
        root_cause = request.POST.get('root_cause', '')
        
        if new_status and new_status != bug.status:
            with transaction.atomic():
                old_status = bug.status
                bug.status = new_status
                bug.root_cause = root_cause
                bug.updated_by = request.logged_user
                bug.save()
                
                # Log the change
                BugActivityLog.objects.create(
                    bug=bug,
                    action='UPDATE_STATUS',
                    performed_by=request.logged_user,
                    old_value=old_status,
                    new_value=new_status
                )
            return redirect('bug_detail', bug_id=bug.id)

    activity_logs = bug.activity_logs.all()
    return render(request, 'bugs/bug_detail.html', {
        'bug': bug, 
        'activity_logs': activity_logs
    })

@custom_login_required
def create_bug(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is a member with 'tester' role
    membership = ProjectMember.objects.filter(project=project, user=request.logged_user).select_related('role').first()
    
    if not membership or membership.role.title != 'tester':
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        bug_type = request.POST.get('type')
        priority = request.POST.get('priority')
        
        with transaction.atomic():
            bug = Bug.objects.create(
                project=project,
                title=title,
                description=description,
                type=bug_type,
                priority=priority,
                created_by=request.logged_user,
                updated_by=request.logged_user,
                status='NEW'
            )
            BugActivityLog.objects.create(
                bug=bug,
                action='CREATE_BUG',
                performed_by=request.logged_user,
                new_value='NEW'
            )
        return redirect('project_detail', project_id=project.id)
        
    return render(request, 'bugs/create_bug.html', {'project': project})

@custom_login_required
def create_project(request):
    # Only superusers can create projects
    if not request.logged_user.is_superuser:
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            with transaction.atomic():
                # 1. Create Project
                project = Project.objects.create(
                    name=name,
                    description=description,
                    created_by=request.logged_user,
                    updated_by=request.logged_user,
                    status='ACTIVE'
                )
                
                # 2. Get or Create Manager Role
                role, created = Role.objects.get_or_create(
                    title='Manager',
                    defaults={'description': 'Project Owner/Manager', 'active': True}
                )
                
                # 3. Add user as member
                ProjectMember.objects.create(
                    project=project,
                    user=request.logged_user,
                    role=role,
                    created_by=request.logged_user,
                    updated_by=request.logged_user
                )
                
                return redirect('dashboard')
                
    return render(request, 'bugs/create_project.html')

@custom_login_required
def manage_members(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Only superusers can manage members for now
    if not request.logged_user.is_superuser:
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        
        if user_id and role_id:
            user_to_add = get_object_or_404(User, id=user_id)
            role_to_assign = get_object_or_404(Role, id=role_id)
            
            # Create or update membership
            ProjectMember.objects.update_or_create(
                project=project,
                user=user_to_add,
                defaults={
                    'role': role_to_assign,
                    'created_by': request.logged_user,
                    'updated_by': request.logged_user
                }
            )
            return redirect('manage_members', project_id=project.id)

            return redirect('manage_members', project_id=project.id)

    members = project.members.exclude(user__is_superuser=True).select_related('user', 'role')
    
    # Users not yet in project
    current_member_ids = members.values_list('user_id', flat=True)
    available_users = User.objects.exclude(id__in=current_member_ids).filter(is_active=True, is_superuser=False)
    
    roles = Role.objects.filter(active=True, title__in=['pm', 'dev', 'tester'])
    
    return render(request, 'bugs/manage_members.html', {
        'project': project,
        'members': members,
        'available_users': available_users,
        'roles': roles
    })

@custom_login_required
def remove_member(request, project_id, user_id):
    # Only superusers can manage members
    if not request.logged_user.is_superuser:
        return render(request, '403.html', status=403)
        
    project = get_object_or_404(Project, id=project_id)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Remove the member record
    ProjectMember.objects.filter(project=project, user=user_to_remove).delete()
    
    return redirect('manage_members', project_id=project.id)
