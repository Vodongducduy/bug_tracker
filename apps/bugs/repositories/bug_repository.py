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

    def get_user_bug_summary(self, user):
        from django.db.models import Count
        # Bugs in projects where user is a member
        user_projects = user.project_memberships.values_list('project_id', flat=True)
        stats = Bug.objects.filter(project_id__in=user_projects).values('status').annotate(total=Count('id'))
        
        summary = {
            'TOTAL': 0,
            'NEW': 0,
            'ASSIGNED': 0,
            'IN_PROGRESS': 0,
            'FIXED': 0,
            'CLOSED': 0,
            'RE_OPENED': 0
        }
        
        total = 0
        for item in stats:
            status = item['status']
            count = item['total']
            if status in summary:
                summary[status] = count
            total += count
            
        summary['TOTAL'] = total
        return summary

    def filter_bugs(self, project, search_query=None, status=None, priority=None, bug_type=None):
        from django.db.models import Q
        bugs = project.bugs.all()
        
        if search_query:
            search_query = search_query.strip()
            bugs = bugs.filter(Q(title__icontains=search_query) | Q(id__icontains=search_query))
        
        if status:
            bugs = bugs.filter(status=status)
            
        if priority:
            bugs = bugs.filter(priority=priority)
            
        if bug_type:
            bugs = bugs.filter(type=bug_type)
            
        return bugs.order_by('-updated_at')
