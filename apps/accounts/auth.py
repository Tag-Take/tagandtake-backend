from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError


class EmailOrUsernameModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            raise ValidationError("No user found with this username or email.")

        if not user.check_password(password):
            raise ValidationError("Incorrect password.")

        if not self.user_can_authenticate(user):
            raise ValidationError("This user account is inactive.")

        return user
