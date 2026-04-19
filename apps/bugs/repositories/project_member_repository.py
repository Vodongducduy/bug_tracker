from apps.bugs.models import ProjectMember

class ProjectMemberRepository:
    def get_membership(self, project, user):
        return ProjectMember.objects.filter(project=project, user=user).select_related('role').first()

    def exists(self, project, user):
        return ProjectMember.objects.filter(project=project, user=user).exists()

    def create(self, project, user, role, action_by):
        return ProjectMember.objects.create(
            project=project,
            user=user,
            role=role,
            created_by=action_by,
            updated_by=action_by
        )

    def update_or_create(self, project, user, role, action_by):
        return ProjectMember.objects.update_or_create(
            project=project,
            user=user,
            defaults={
                'role': role,
                'created_by': action_by,
                'updated_by': action_by
            }
        )

    def delete(self, project, user):
        ProjectMember.objects.filter(project=project, user=user).delete()

    def get_all_by_project(self, project):
        return project.members.exclude(user__is_superuser=True).select_related('user', 'role')
