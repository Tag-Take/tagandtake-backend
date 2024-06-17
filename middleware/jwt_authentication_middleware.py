from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt

User = get_user_model()  # Ensure User model is correctly referenced


def get_user_from_token(request):
    token = request.COOKIES.get("access_token")  # Changed from 'jwt' to 'access_token'
    if not token:
        return AnonymousUser()

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload["user_id"])
        if not user.is_active:
            raise AuthenticationFailed("User is inactive")
        return user
    except User.DoesNotExist:
        raise AuthenticationFailed("No such user")
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired")
    except jwt.DecodeError:
        raise AuthenticationFailed("Error decoding signature")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")


class JWTAuthenticationMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        # Ensures that the user is evaluated lazily, so database hits are minimized
        request.user = SimpleLazyObject(lambda: get_user_from_token(request))
        return self.get_response(request)
