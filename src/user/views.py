import json

import bcrypt
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpRequest
from django.views import View

from user.manager import UserManager
from user.models import User
from utils.logger import logger
from utils.mixin import CsrfExemptMixin


class UserRegister(CsrfExemptMixin, View, UserManager):

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data: json = json.loads(request.body)
            try:
                username: str = data['username']
                email: str = data['email']
                password: str = data['password']
            except KeyError:
                return JsonResponse(
                    {
                        "error": "Required params in body json: 'username', 'email', 'password'"
                    }
                )
            home_page = data.get('home_page', '')

            if not username.isalnum():  # username Validity Check
                return JsonResponse(
                    {
                        "error": "Username must contain only alphanumeric characters"
                    }, status=500
                )

            try:
                if User.objects.get(username=username):  # Check if there is such user
                    return JsonResponse(
                        {
                            'error': 'User with this username already exists'
                        }, status=500
                    )
            except ObjectDoesNotExist:  # If there is no such username -> check such email
                try:
                    if User.objects.get(email=email):
                        return JsonResponse(
                            {
                                'error': 'User with this email already exists'
                            }, status=500
                        )
                except ObjectDoesNotExist:  # If there is no such user -> register user
                    user_data: dict = self.register_user(username, email, password, home_page)
                    return JsonResponse(
                        {
                            "success": True,
                            "user": user_data
                        }
                    )
        except Exception as e:
            logger.error(f"An unexpected error occurred while creating a user | {e}")
            return JsonResponse(
                {
                    "error": f"An unexpected error occurred while creating a user | {str(e)}"
                }, status=500
            )


class UserLogin(CsrfExemptMixin, View, UserManager):

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data: json = json.loads(request.body)

            try:
                username: str = data['username']
                password: str = data['password']
            except KeyError:
                return JsonResponse(
                    {
                        "error": "Required params in body json: 'username', 'password'"
                    }
                )

            try:
                user = User.objects.get(username=username)  # Check if there is such user

                hashed_password = user.password
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):  # Check password match
                    access_token: str = self.login(username)

                    return JsonResponse(
                        {
                            "success": True,
                            "user": {
                                "id": user.pk,
                                "username": user.username,
                                "email": user.email
                            },
                            "access_token": access_token
                        }
                    )
                else:
                    return JsonResponse(
                        {
                            "error": "Invalid password"
                        }, status=500
                    )
            except ObjectDoesNotExist:
                return JsonResponse(
                    {
                        'error': 'There is no such user with such username'
                    }, status=500
                )
        except Exception as e:
            logger.error(f"An unexpected error occurred while login user | {e}")
            return JsonResponse(
                {
                    "error": f"An unexpected error occurred while login user | {str(e)}"
                }, status=500
            )
