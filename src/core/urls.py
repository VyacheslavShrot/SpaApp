from django.urls import path

from core.views import CommentView, CaptchaView

urlpatterns = [
    path('post', CommentView.as_view(), name='comment'),
    path('captcha/create', CaptchaView.as_view(), name='captcha'),
]
