from django.db import models

from config.models import BaseModel
from user.models import User


class Comment(BaseModel):
    captcha = models.BooleanField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"{self.user} | {self.text}"
