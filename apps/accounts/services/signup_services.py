import re

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from apps.common.utils.db import create_instance_with_related_models
from apps.stores.services.store_create_services import (
    create_default_store_item_categories_and_conditions,
)
from apps.stores.models import (
    StoreProfile,
    StoreAddress,
    StoreNotificationPreferences,
    StoreOpeningHours,
)
from apps.members.models import MemberProfile, MemberNotificationPreferences


User = get_user_model()


class SignupService:

    @staticmethod
    @transaction.atomic
    def create_store_user(
        validated_data, store_profile_data, address_data, opening_hours_data
    ):
        related_data = {
            StoreProfile: {
                "foreign_key_name": "user",
                "related_model": User,
                "data": store_profile_data,
            },
            StoreAddress: {
                "foreign_key_name": "store",
                "related_model": StoreProfile,
                "data": address_data,
            },
            StoreOpeningHours: {
                "foreign_key_name": "store",
                "related_model": StoreProfile,
                "data": opening_hours_data,
            },
            StoreNotificationPreferences: {
                "foreign_key_name": "store",
                "related_model": StoreProfile,
                "data": {},
            },
        }
        user = create_instance_with_related_models(User, validated_data, related_data)
        store_profile = StoreProfile.objects.get(user=user)

        create_default_store_item_categories_and_conditions(store_profile)

        return user

    @staticmethod
    def create_member_user(validated_data):
        related_data = {
            MemberProfile: {
                "foreign_key_name": "user",
                "related_model": User,
                "data": {},
            },
            MemberNotificationPreferences: {
                "foreign_key_name": "member",
                "related_model": MemberProfile,
                "data": {},
            },
        }

        return create_instance_with_related_models(User, validated_data, related_data)


class UsernameValidator:
    def __init__(self, min_length=3, max_length=30):
        self.min_length = min_length
        self.max_length = max_length
        self.username_regex = re.compile(
            r"^[a-z0-9_]+$"
        )  # Allow letters, numbers, and underscores only

    def __call__(self, value):
        if len(value) < self.min_length or len(value) > self.max_length:
            raise ValidationError(
                _(
                    f"Username must be between {self.min_length} and {self.max_length} characters long."
                ),
                code="invalid_length",
            )

        if not self.username_regex.match(value):
            raise ValidationError(
                _(
                    "Username can only contain lowercase letters, numbers, and underscores."
                ),
                code="invalid_characters",
            )

        reserved_usernames = ["admin", "root", "system"]
        if value.lower() in reserved_usernames:
            raise ValidationError(
                _(f"The username '{value}' is reserved and cannot be used."),
                code="reserved_username",
            )
