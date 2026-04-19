from apps.accounts.models import Role

class RoleRepository:
    def get_or_create_by_title(self, title, defaults=None):
        return Role.objects.get_or_create(title=title, defaults=defaults)

    def get_by_id(self, role_id):
        try:
            return Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return None

    def get_active_roles(self, titles):
        return Role.objects.filter(active=True, title__in=titles)
