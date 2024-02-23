import json

import bcrypt as bcrypt

from user.models import User


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
