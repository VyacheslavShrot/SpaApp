from django.urls import path

from core.views import CommentView, CaptchaView, CommentRoom

urlpatterns = [
    path('post', CommentView.as_view(), name='comment'),
    path('captcha/create', CaptchaView.as_view(), name='captcha'),
    path("<str:comment_id>/", CommentRoom.as_view(), name="comment-room"),
]
