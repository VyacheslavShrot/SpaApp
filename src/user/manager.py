import json
from datetime import timedelta

import bcrypt as bcrypt

from user.models import User
from utils.token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token


class UserManager:

    @staticmethod
    def register_user(data: json) -> dict:
        password: str = data['password']
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        password = password_hash.decode('utf-8')

        user = User.objects.create(
            username=data.get('username'),
            password=password,
            email=data['email'],
            home_page=data.get('home_page', ''),
        )

        return {
            "pk": user.pk,
            "username": user.username,
            "email": user.email,
            "home_page": user.home_page,
            "created_at": user.created_at.isoformat()
        }

    @staticmethod
    def login(username) -> str:
        token_data: dict = {"sub": username}

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(token_data, access_token_expires)
