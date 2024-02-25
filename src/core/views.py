import json
from io import BytesIO

from django.core.cache import cache
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.manager import CaptchaManager
from core.models import Comment
from user.models import User
from utils.logger import logger
from utils.token import check_login


class CaptchaView(View, CaptchaManager):

    # todo - Need to DELETE in PROD version and pass csrf token from frontend
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @check_login
    def post(self, request: HttpRequest, username: str) -> HttpResponse:
        try:
            captcha_image_bytes: BytesIO = self.create_captcha()

            return HttpResponse(
                captcha_image_bytes,
                content_type='image/png'
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while creating captcha | {e}")
            return JsonResponse(
                {
                    "error": f"An unexpected error occurred while creating captcha | {str(e)}"
                }, status=500
            )


class CommentView(View):

    # todo - Need to DELETE in PROD version and pass csrf token from frontend
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @check_login
    def post(self, request: HttpRequest, username: str) -> JsonResponse:
        try:
            data: json = json.loads(request.body)
            try:
                text: str = data['text']
                user_input_captcha: str = data['captcha_text']
            except KeyError:
                return JsonResponse(
                    {
                        "error": "Required params in body json: 'captcha_text', 'text'"
                    }
                )

            captcha_text: str = cache.get('captcha_text')
            if not captcha_text:
                return JsonResponse(
                    {
                        "error": "There is no generated captcha"
                    }, status=500
                )
            if not captcha_text.lower() == user_input_captcha.lower():
                return JsonResponse(
                    {
                        "error": "Entered text is not equal to captcha text"
                    }, status=500
                )

            user = User.objects.get(username=username)

            comment = Comment.objects.create(
                captcha=True,
                text=text,
                user=user
            )

            return JsonResponse(
                {
                    "success": True,
                    "comment": {
                        "id": comment.pk,
                        "captcha": comment.captcha,
                        "text": comment.text,
                        "created_at": comment.created_at,
                        "user": {
                            "id": user.pk,
                            "username": user.username,
                            "email": user.email
                        }
                    }
                }
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while post comment | {e}")
            return JsonResponse(
                {
                    "error": f"An unexpected error occurred while post comment | {str(e)}"
                }, status=500
            )
