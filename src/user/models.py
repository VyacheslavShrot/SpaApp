from django.db import models

from config.models import BaseModel


class User(BaseModel):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=20)
    email = models.EmailField()
    home_page = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
