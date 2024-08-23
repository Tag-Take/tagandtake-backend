import datetime
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from apps.accounts.models import User



def create_error_response(message: str, errors: list, status_code: status):
    return Response(
        {
            "status": "error",
            "message": message,
            "data": {},
            "errors": errors,
        },
        status=status_code,
    )


def create_success_response(message: str, errors: list, status_code: status):
    return Response(
        {
            "status": "success",
            "message": message,
            "data": data,
            "errors": {},
        },
        status=status_code,
    )


def extract_error_messages(exception: any):
    """
    Extract error messages from different types of exceptions, ensuring JSON-serializable output.
    Handles DRF and Django ValidationErrors, as well as other exception types.
    """
    if isinstance(exception, serializers.ValidationError):
        detail = exception.detail

        if isinstance(detail, dict):
            return detail

        if isinstance(detail, list):
            return [str(error) for error in detail]

        return [str(detail)]

    if isinstance(exception, DjangoValidationError):
        if hasattr(exception, "message_dict"):
            return exception.message_dict

        if hasattr(exception, "messages"):
            return [str(msg) for msg in exception.messages]

    return [str(exception)]


def flatten_errors(detail: any):
    """
    Recursively flatten error messages, ensuring JSON-serializable output.
    Handles nested lists and dictionaries and returns a flat list of error messages.
    """
    if isinstance(detail, list):
        errors = []
        for item in detail:
            errors.extend(flatten_errors(item))
        return errors

    if isinstance(detail, dict):
        errors = []
        for key, value in detail.items():
            errors.extend(flatten_errors(value))
        return errors

    return [str(detail)]


class JWTCookieHandler:
    def __init__(self, response: Response):
        self.response: Response = response

    def set_jwt_cookies(self, access_token: AccessToken, refresh_token=None):
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

        self.response.delete_cookie("refresh_token", path="/")
        self.response.delete_cookie("access_token", path="/")

        return self.response

    @staticmethod
    def _generate_tokens(user: User):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return access_token, refresh_token
