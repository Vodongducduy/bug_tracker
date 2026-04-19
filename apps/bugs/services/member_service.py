from apps.bugs.repositories.project_repository import ProjectRepository
from apps.bugs.repositories.project_member_repository import ProjectMemberRepository
from apps.bugs.repositories.user_repository import UserRepository
from apps.bugs.repositories.role_repository import RoleRepository

class ProjectMemberService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        user_repository: UserRepository,
        role_repository: RoleRepository
    ):
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository
        self.user_repository = user_repository
        self.role_repository = role_repository

    def get_manage_members_context(self, project_id, user):
        if not user.is_superuser:
            return None, 'FORBIDDEN'
            
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None, 'NOT_FOUND'
            
        members = self.project_member_repository.get_all_by_project(project)
        current_member_ids = members.values_list('user_id', flat=True)
        available_users = self.user_repository.get_available_for_project(current_member_ids)
        roles = self.role_repository.get_active_roles(['pm', 'dev', 'tester'])
        
        return {
            'project': project,
            'members': members,
            'available_users': available_users,
            'roles': roles
        }, 'OK'

    def manage_member(self, project_id, user_id, role_id, action_by):
        if not action_by.is_superuser:
            return None, 'FORBIDDEN'
            
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None, 'NOT_FOUND'
            
        user_to_add = self.user_repository.get_by_id(user_id)
        role_to_assign = self.role_repository.get_by_id(role_id)
        
        if not user_to_add or not role_to_assign:
            return project, 'INVALID_DATA'
            
        self.project_member_repository.update_or_create(
            project=project,
            user=user_to_add,
            role=role_to_assign,
            action_by=action_by
        )
        return project, 'OK'

    def remove_member(self, project_id, user_id, action_by):
        if not action_by.is_superuser:
            return None, 'FORBIDDEN'
            
        project = self.project_repository.get_by_id(project_id)
        user_to_remove = self.user_repository.get_by_id(user_id)
        
        if not project or not user_to_remove:
            return None, 'NOT_FOUND'
            
        self.project_member_repository.delete(project, user_to_remove)
        return project, 'OK'
