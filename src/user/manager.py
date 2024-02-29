import bcrypt as bcrypt
from celery.result import AsyncResult
from django.core.cache import cache

from user.models import User
from utils.token import create_access_token


class UserManager:

    @staticmethod
    def hash_password(password: str) -> str:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        return password_hash.decode('utf-8')

    def register_user(self, username: str, email: str, password: str, home_page: str) -> dict:
        password = self.hash_password(password)

        user = User.objects.create(
            username=username,
            password=password,
            email=email,
            home_page=home_page,
        )

        return {
            "pk": user.pk,
            "username": user.username,
            "email": user.email,
            "home_page": user.home_page,
            "created_at": user.created_at.isoformat()
        }

    @staticmethod
    def token_save_to_cache(token: str) -> None:
        cache.set(f'token', token, 7200)

    def login(self, username) -> str:
        token_data: dict = {"sub": username}

        token_task: AsyncResult = create_access_token.delay(token_data)
        token: str = token_task.get()

        self.token_save_to_cache(token)

        return token
