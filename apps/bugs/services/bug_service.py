from django.db import transaction
from apps.bugs.repositories.project_repository import ProjectRepository
from apps.bugs.repositories.project_member_repository import ProjectMemberRepository
from apps.bugs.repositories.bug_repository import BugRepository
from apps.bugs.repositories.bug_activity_log_repository import BugActivityLogRepository

class BugService:
    def __init__(
        self,
        bug_repository: BugRepository,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        bug_activity_log_repository: BugActivityLogRepository
    ):
        self.bug_repository = bug_repository
        self.project_repository = project_repository
        self.project_member_repository = project_member_repository
        self.bug_activity_log_repository = bug_activity_log_repository

    def get_bug_detail(self, bug_id, user):
        bug = self.bug_repository.get_by_id(bug_id)
        if not bug:
            return None, 'NOT_FOUND', None
            
        if not self.project_member_repository.exists(bug.project, user):
            return bug, 'FORBIDDEN', None
            
        activity_logs = self.bug_activity_log_repository.get_by_bug(bug)
        return bug, 'OK', activity_logs

    def update_bug_status(self, bug, new_status, root_cause, user):
        if not new_status or new_status == bug.status:
            return False
            
        with transaction.atomic():
            old_status = bug.status
            bug = self.bug_repository.update_status(bug, new_status, root_cause, user)
            
            self.bug_activity_log_repository.create(
                bug=bug,
                action='UPDATE_STATUS',
                performed_by=user,
                old_value=old_status,
                new_value=new_status
            )
        return True

    def create_bug(self, project_id, title, description, bug_type, priority, user):
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None, 'NOT_FOUND'
            
        membership = self.project_member_repository.get_membership(project, user)
        if not membership or membership.role.title != 'tester':
            return project, 'FORBIDDEN'

        with transaction.atomic():
            bug = self.bug_repository.create(project, title, description, bug_type, priority, user)
            
            self.bug_activity_log_repository.create(
                bug=bug,
                action='CREATE_BUG',
                performed_by=user,
                new_value='NEW'
            )
        return project, 'CREATED'
