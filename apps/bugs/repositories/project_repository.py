from apps.bugs.models import Project

class ProjectRepository:
    def get_user_projects(self, user):
        return Project.objects.filter(members__user=user)

    def get_by_id(self, project_id):
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

    def create(self, name, description, user):
        return Project.objects.create(
            name=name,
            description=description,
            created_by=user,
            updated_by=user,
            status='ACTIVE'
        )
