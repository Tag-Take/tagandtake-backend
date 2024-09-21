import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.constants import (
    EMAIL,
    USERNAME,
    MEMBER,
    IS_STAFF,
    IS_SUPERUSER,
    CUSTOM_USER_SET,
)


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=MEMBER, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault(IS_STAFF, True)
        extra_fields.setdefault(IS_SUPERUSER, True)

        return self.create_user(username, email, password, role=MEMBER, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class Roles(models.TextChoices):
        MEMBER = "member", _("Member")
        STORE = "store", _("Store")

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.MEMBER,
    )
    is_active = models.BooleanField(default=False)
    activation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(Group, related_name=CUSTOM_USER_SET)
    user_permissions = models.ManyToManyField(Permission, related_name=CUSTOM_USER_SET)

    objects = UserManager()

    USERNAME_FIELD = USERNAME
    EMAIL_FIELD = EMAIL
    REQUIRED_FIELDS = [EMAIL]

    def __str__(self):
        return self.email
