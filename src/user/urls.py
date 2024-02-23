from django.urls import path

from user.views import UserRegister

urlpatterns = [
    path('create', UserRegister.as_view(), name='user-create'),
]
