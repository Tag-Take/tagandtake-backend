from django.contrib.auth import get_user_model
from django.db import transaction
from apps.common.utils.db import create_instance_with_related_models
from apps.stores.services.store_create_services import create_store_item_categories_and_conditions
from apps.stores.models import (
    StoreProfile,
    StoreAddress,
    StoreNotificationPreferences,
    StoreOpeningHours,
)
from apps.members.models import MemberProfile, MemberNotificationPreferences
from apps.emails.services.email_senders import StoreEmailSender, MemberEmailSender


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

        create_store_item_categories_and_conditions(store_profile)

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
