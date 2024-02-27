import json
import random
from io import BytesIO

from captcha.image import ImageCaptcha
from django.core.cache import cache

from core.models import Comment, Messages
from user.models import User


class CoreManager:

    @staticmethod
    def get_body(data: json, *args: str) -> dict:
        result = {}
        for key in args:
            result[key] = data[key]

        return result

    @staticmethod
    def get_user(search_field: str, value) -> User:
        return User.objects.get(**{search_field: value})

    @staticmethod
    def create_comment(text: str, user: User) -> Comment:
        return Comment.objects.create(
            captcha=True,
            text=text,
            user=user
        )

    @staticmethod
    def get_comment(search_field: str, value) -> Comment:
        return Comment.objects.get(**{search_field: value})

    @staticmethod
    def create_message(message: str, current_user: User, comment: Comment) -> Messages:
        return Messages.objects.create(
            message=message,
            user=current_user,
            comment=comment
        )


class CaptchaManager:

    @staticmethod
    def generate_captcha_text() -> str:
        captcha_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(random.choice(captcha_characters) for _ in range(6))

    @staticmethod
    def captcha_text_save_to_cache(captcha_text: str) -> None:
        #  todo - Set captcha_text to save
        cache.set(f'captcha_text', 'ABC', 200)

    def create_captcha(self) -> BytesIO:
        captcha_text = self.generate_captcha_text()

        self.captcha_text_save_to_cache(captcha_text)

        image = ImageCaptcha()
        return image.generate(captcha_text)
