import json
from io import BytesIO

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from core.manager import CaptchaManager, CoreManager
from utils.logger import logger
from utils.mixin import CsrfExemptMixin
from utils.token import check_login


class CaptchaView(CsrfExemptMixin, View, CaptchaManager):

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


class CommentRoom(CsrfExemptMixin, View):

    @check_login
    def get(self, request: HttpRequest, username: str, comment_id: str):
        cache.set('username', username, 7200)
        return render(request, "room.html", {"comment_id": comment_id})


class CommentView(CsrfExemptMixin, View, CoreManager):

    @check_login
    def get(self, request: HttpRequest, username: str) -> JsonResponse:
        try:
            username_filter = request.GET.get('username', None)
            email_filter = request.GET.get('email', None)
            date_filter = request.GET.get('date', None)

            if date_filter:
                if date_filter not in ["new", "old"]:
                    return JsonResponse(
                        {
                            "error": "'new' or 'old' should be in this parameter"
                        }
                    )

            try:
                if username_filter and email_filter:
                    if self.get_user("username", username_filter) == self.get_user("email", email_filter):
                        return JsonResponse(
                            {
                                "error": "'email' and 'username' refer to the same user"
                            }
                        )

                comments = self.get_filter_comments(
                    username_filter,
                    email_filter,
                    date_filter
                )
            except ObjectDoesNotExist:
                return JsonResponse(
                    {
                        "error": "There is no such comments with such filters"
                    }
                )
            return JsonResponse(
                {
                    "comments": comments
                }
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while get comments | {e}")
            return JsonResponse(
                {
                    "error": f"An unexpected error occurred while get comments | {str(e)}"
                }, status=500
            )

    @check_login
    def post(self, request: HttpRequest, username: str) -> JsonResponse:
        try:
            data: json = json.loads(request.body)
            try:
                body: dict = self.get_body(data, 'text', 'captcha_text')
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
            if not captcha_text.lower() == body.get('captcha_text').lower():
                return JsonResponse(
                    {
                        "error": "Entered text is not equal to captcha text"
                    }, status=500
                )

            user = self.get_user('username', username)
            comment = self.create_comment(body.get('text'), user)

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
