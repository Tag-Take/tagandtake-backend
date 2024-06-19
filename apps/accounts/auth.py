# authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt

from django.contrib.auth import get_user_model

User = get_user_model()


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if getattr(request, "skip_authentication", False):
            return None

        token = request.COOKIES.get("access_token")
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            if not user.is_active:
                raise AuthenticationFailed("User is inactive")
            return (user, token)
        except User.DoesNotExist:
            raise AuthenticationFailed("No such user")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.DecodeError:
            raise AuthenticationFailed("Error decoding signature")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
