from apps.bugs.models import Bug

class BugRepository:
    def get_by_project(self, project):
        return project.bugs.all().order_by('-updated_at')

    def get_by_id(self, bug_id):
        try:
            return Bug.objects.get(id=bug_id)
        except Bug.DoesNotExist:
            return None

    def create(self, project, title, description, bug_type, priority, user):
        return Bug.objects.create(
            project=project,
            title=title,
            description=description,
            type=bug_type,
            priority=priority,
            created_by=user,
            updated_by=user,
            status='NEW'
        )

    def update_status(self, bug, new_status, root_cause, user):
        bug.status = new_status
        bug.root_cause = root_cause
        bug.updated_by = user
        bug.save()
        return bug
