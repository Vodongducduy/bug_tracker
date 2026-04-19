from apps.accounts.models import User

class UserRepository:
    def get_available_for_project(self, current_member_ids):
        return User.objects.exclude(id__in=current_member_ids).filter(is_active=True, is_superuser=False)
    
    def get_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
