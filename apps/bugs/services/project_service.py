from django.db import transaction
from apps.bugs.repositories.project_repository import ProjectRepository
from apps.bugs.repositories.project_member_repository import ProjectMemberRepository
from apps.bugs.repositories.bug_repository import BugRepository
from apps.bugs.repositories.role_repository import RoleRepository

class ProjectService:
    def __init__(
        self, 
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        bug_repository: BugRepository,
        role_repository: RoleRepository
    ):
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository
        self.bug_repository = bug_repository
        self.role_repository = role_repository

    def get_dashboard_projects(self, user):
        return self.project_repository.get_user_projects(user)

    def get_project_detail(self, project_id, user, filters=None):
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None, None, None

        # Check membership
        membership = self.project_member_repository.get_membership(project, user)
        if not membership and not user.is_superuser:
            return project, 'FORBIDDEN', None

        user_role = membership.role.title if membership else None
        
        if filters:
            bugs = self.bug_repository.filter_bugs(
                project, 
                search_query=filters.get('q'),
                status=filters.get('status'),
                priority=filters.get('priority'),
                bug_type=filters.get('type')
            )
        else:
            bugs = self.bug_repository.get_by_project(project)
        
        return project, user_role, bugs

    def create_project(self, name, description, user):
        if not name:
            return None
            
        with transaction.atomic():
            project = self.project_repository.create(name, description, user)
            
            role, _ = self.role_repository.get_or_create_by_title(
                'Manager',
                defaults={'description': 'Project Owner/Manager', 'active': True}
            )
            
            self.project_member_repository.create(project, user, role, user)
            
        return project
