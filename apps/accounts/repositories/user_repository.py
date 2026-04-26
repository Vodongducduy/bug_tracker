from apps.accounts.models import User

class UserRepository:
    def get_by_username(self, username):
        try:
            return User.objects.get(username=username)
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

    def get_all(self):
        return User.objects.all().order_by('-date_joined')

    def get_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def update_status(self, user_id, is_active):
        user = self.get_by_id(user_id)
        if user:
            user.is_active = is_active
            user.save()
            return user
        return None
