import datetime
from datetime import datetime

from django.conf import settings

from rest_framework.response import Response
from rest_framework import status
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


class JWTHandler:

    @staticmethod
    def set_jwt_cookies(response, refresh_token: RefreshToken):
        response.set_cookie(
            REFRESH_TOKEN,
            refresh_token,
            expires=datetime.utcnow() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SAME_SITE_COOKIE,
            domain=settings.DOMAIN,
        )
        return response

    @staticmethod
    def blacklist_token(self, refresh_token=None):
        refresh_token_obj = RefreshToken(refresh_token)
        refresh_token_obj.blacklist()
