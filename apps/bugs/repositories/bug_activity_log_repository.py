from apps.bugs.models import BugActivityLog

class BugActivityLogRepository:
    def create(self, bug, action, performed_by, new_value, old_value=None):
        return BugActivityLog.objects.create(
            bug=bug,
            action=action,
            performed_by=performed_by,
            old_value=old_value,
            new_value=new_value
        )
    
    def get_by_bug(self, bug):
        return bug.activity_logs.all()
