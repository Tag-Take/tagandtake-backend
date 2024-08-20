import datetime
from datetime import datetime

from django.conf import settings

from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def create_error_response(message, errors, status_code):
    return Response(
        {
            "status": "error",
            "message": message,
            "data": {},
            "errors": errors,
        },
        status=status_code,
    )


def create_success_response(message, data, status_code):
    return Response(
        {
            "status": "success",
            "message": message,
            "data": data,
            "errors": {},
        },
        status=status_code,
    )


class JWTCookieHandler:
    def __init__(self, response):
        self.response: Response = response

    def set_jwt_cookies(self, access_token, refresh_token=None):
        self.response.set_cookie(
            "access_token",
            access_token,
            expires=datetime.utcnow() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SAME_SITE_COOKIE,
            domain=settings.DOMAIN,
        )
        if refresh_token:
            self.response.set_cookie(
                "refresh_token",
                refresh_token,
                expires=datetime.utcnow() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
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

        self.response.delete_cookie("refresh_token", path="/")
        self.response.delete_cookie("access_token", path="/")

        return self.response

    @staticmethod
    def _generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return access_token, refresh_token
