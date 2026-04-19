from django.contrib.auth.hashers import check_password, make_password
from apps.accounts.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate(self, username, password):
        user = self.user_repository.get_by_username(username)
        if user and check_password(password, user.password):
            return user
        return None

    def register_user(self, username, email, password, first_name, last_name):
        hashed_password = make_password(password)
        return self.user_repository.create_user(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
