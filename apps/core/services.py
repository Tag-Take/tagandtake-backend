from apps.core.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class UserService:
    @staticmethod
    def register_user(email, username, password, is_store=False, is_member=False):
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            is_store=is_store,
            is_member=is_member
        )
        return user
