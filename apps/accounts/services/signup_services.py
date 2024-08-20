from django.contrib.auth import get_user_model
from apps.common.utils.db import create_instance_with_related_models
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

        return create_instance_with_related_models(User, validated_data, related_data)

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
