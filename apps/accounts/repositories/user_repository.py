from apps.accounts.models import User

class UserRepository:
    def get_by_username(self, username):
        try:
            return User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return None

    def create_user(self, username, email, password, first_name, last_name, is_active=True, is_staff=False, is_superuser=False):
        return User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
