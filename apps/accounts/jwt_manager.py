from datetime import datetime
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from apps.common.constants import REFRESH_TOKEN, ACCESS_TOKEN

class JWTManager:
    @staticmethod
    def set_refresh_token_cookie(response, refresh_token: RefreshToken):
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
    def clear_refresh_token_cookie(response):
        response.delete_cookie(
            REFRESH_TOKEN,
            domain=settings.DOMAIN,
            samesite=settings.SAME_SITE_COOKIE,
        )
        return response

    @staticmethod
    def blacklist_refresh_token(refresh_token=None):
        refresh_token_obj = RefreshToken(refresh_token)
        refresh_token_obj.blacklist()

    @staticmethod
    def generate_tokens(user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        
        return str(access_token), str(refresh_token)