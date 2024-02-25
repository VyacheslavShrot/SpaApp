import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any

from django.core.cache import cache
from django.http import HttpRequest, JsonResponse
from jose import jwt, JWTError

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def check_login(func) -> JsonResponse | Any:
    @wraps(func)
    def wrapper(self, request: HttpRequest, *args, **kwargs):
        try:
            token: str = cache.get('token')
            if not token:
                try:
                    token = request.headers.get("Authorization").split()[1]
                except AttributeError:
                    return JsonResponse(
                        {
                            "error": "Authorization header is missing"
                        }, status=500
                    )

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            username = payload.get("sub")
            if username is None:
                return JsonResponse(
                    {
                        "error": "Invalid token"
                    }, status=401
                )
            else:
                return func(self, request, username, *args, **kwargs)
        except KeyError:
            return JsonResponse(
                {
                    "error": "Authorization header is missing"
                }, status=401
            )
        except JWTError:
            return JsonResponse(
                {
                    "error": "Invalid token"
                }, status=401
            )
    return wrapper
