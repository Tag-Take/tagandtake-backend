import datetime
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from apps.common.constants import (
    ACCESS_TOKEN,
    REFRESH_TOKEN,
    STATUS,
    DATA,
    MESSAGE,
    SUCCESS,
    ERROR,
    ERRORS,
)
from apps.accounts.models import User


def create_error_response(message: str, errors: list, status_code: status):
    return Response(
        {
            STATUS: ERROR,
            MESSAGE: message,
            DATA: {},
            ERRORS: errors,
        },
        status=status_code,
    )


def create_success_response(message: str, data: list[dict], status_code: status):
    return Response(
        {
            STATUS: SUCCESS,
            MESSAGE: message,
            DATA: data,
            ERRORS: {},
        },
        status=status_code,
    )


class JWTCookieHandler:
    def __init__(self, response: Response):
        self.response: Response = response

    def set_jwt_cookies(self, access_token: AccessToken, refresh_token=None):
        self.response.set_cookie(
            ACCESS_TOKEN,
            access_token,
            expires=datetime.utcnow() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SAME_SITE_COOKIE,
            domain=settings.DOMAIN,
        )
        if refresh_token:
            self.response.set_cookie(
                REFRESH_TOKEN,
                refresh_token,
                expires=datetime.utcnow()
                + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SAME_SITE_COOKIE,
                domain=settings.DOMAIN,
            )
        return self.response

    def delete_jwt_cookies(self, refresh_token=None):
        if refresh_token:
            refresh_token_obj = RefreshToken(refresh_token)
            refresh_token_obj.blacklist()

        self.response.delete_cookie(REFRESH_TOKEN, path="/")
        self.response.delete_cookie(ACCESS_TOKEN, path="/")

        return self.response

    @staticmethod
    def _generate_tokens(user: User):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return access_token, refresh_token
