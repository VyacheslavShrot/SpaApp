import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from user.manager import UserManager
from user.models import User
from utils.logger import logger


class UserRegister(View, UserManager):

    # todo - Need to DELETE in PROD version and pass csrf token from frontend
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            data = json.loads(request.body)

            username = data['username']
            email = data['email']

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
                    user_data: dict = self.register_user(data)
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
