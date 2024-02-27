import json
import random
from io import BytesIO

from captcha.image import ImageCaptcha
from django.core.cache import cache
from django.db.models import QuerySet
from django.forms import model_to_dict

from core.models import Comment, Messages
from user.models import User

_COMMENT_FIELDS = [
    'id',
    'captcha',
    'text',
    'created_at',
    'user'
]


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
    def format_comments(comments: QuerySet) -> list:
        comments_list = []

        for comment in comments:
            comment_dict = model_to_dict(comment, fields=_COMMENT_FIELDS)
            comment_dict['created_at'] = comment.created_at.strftime('%Y-%m-%d %H:%M:%S')

            comments_list.append(comment_dict)

        return comments_list

    @staticmethod
    def sort_comments(comments: list, reverse: bool) -> list:
        return sorted(comments, key=lambda x: x['created_at'], reverse=reverse)

    def get_all_comments(self) -> list:
        comments: QuerySet = Comment.objects.all()
        return self.format_comments(comments)

    def get_filter_comments(
            self,
            username: str = None,
            email: str = None,
            date: str = None
    ) -> list:
        filtered_comments = []

        if username:
            user_by_username: User = self.get_user("username", username)
            comments: QuerySet = Comment.objects.filter(user=user_by_username)

            for comment in self.format_comments(comments):
                filtered_comments.append(comment)

        if email:
            user_by_email: User = self.get_user("email", email)
            comments: QuerySet = Comment.objects.filter(user=user_by_email)

            for comment in self.format_comments(comments):
                filtered_comments.append(comment)

        if date:
            if date == "new":
                filtered_comments = (
                    self.sort_comments(filtered_comments, True) if username or email else
                    self.sort_comments(self.get_all_comments(), True)
                )
            elif date == "old":
                filtered_comments = (
                    self.sort_comments(filtered_comments, False) if username or email else
                    self.sort_comments(self.get_all_comments(), False)
                )

        return filtered_comments if username or email or date else self.get_all_comments()

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
