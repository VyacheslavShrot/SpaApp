import random
from io import BytesIO

from captcha.image import ImageCaptcha
from django.core.cache import cache


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
