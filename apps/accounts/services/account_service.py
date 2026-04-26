from django.contrib.auth.hashers import make_password
from apps.accounts.repositories.user_repository import UserRepository

class AccountService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_all_accounts(self):
        return self.user_repository.get_all()

    def create_account(self, username, email, password, first_name, last_name, is_superuser=False):
        hashed_password = make_password(password)
        return self.user_repository.create_user(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser
        )

    def toggle_account_status(self, user_id):
        user = self.user_repository.get_by_id(user_id)
        if user:
            new_status = not user.is_active
            return self.user_repository.update_status(user_id, new_status)
        return None
