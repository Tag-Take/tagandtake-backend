from django.db import transaction

from rest_framework import serializers

from apps.common.s3.s3_utils import S3Service
from apps.common.s3.s3_config import get_store_profile_photo_key
from apps.accounts.models import User
from apps.items.models import ItemCategory, ItemCondition
from apps.stores.models import (
    StoreItemCategory,
    StoreItemCondition,
    StoreAddress,
    StoreOpeningHours,
    StoreNotificationPreferences,
)
from apps.stores.models import StoreProfile


class StoreService:
    @staticmethod
    def get_store(store_id: int):
        try:
            return StoreProfile.objects.get(id=store_id)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError("Store does not exist.")

    @staticmethod
    def create_store_profile(user: User, store_profile_data: dict):
        try:
            return StoreProfile.objects.create(user=user, **store_profile_data)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create store profile: {e}")

    @staticmethod
    def create_store_address(store: StoreProfile, address_data: dict):
        try:
            return StoreAddress.objects.create(store=store, **address_data)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create store address: {e}")

    @staticmethod
    def create_store_opening_hours(store: StoreProfile, opening_hours_data: dict):
        try:
            return StoreOpeningHours.objects.create(store=store, **opening_hours_data)
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to create store opening hours: {e}"
            )

    @staticmethod
    def update_store_profile_photo(store: StoreProfile, file):
        profile_photo_url = StoreService.upload_profile_photo_to_s3(store, file)
        store = StoreService.save_profile_photo_url(store, profile_photo_url)
        return store

    @staticmethod
    def save_profile_photo_url(store: StoreProfile, image_url: str):
        try:
            store.profile_photo_url = image_url
            store.save()
            return store
        except Exception as e:
            raise serializers.ValidationError(f"Failed to save profile photo url: {e}")

    @staticmethod
    def upload_profile_photo_to_s3(store: StoreProfile, file):
        try:
            key = get_store_profile_photo_key(store)
            image_url = S3Service().upload_image(file, key)
            return image_url
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to upload profile photo to s3: {e}"
            )

    @staticmethod
    def delete_store_profile_photo(store: StoreProfile):
        StoreService.delete_profile_photo_from_s3(store)
        store = StoreService.delete_profile_photo_url(store)
        return store

    @staticmethod
    def delete_profile_photo_url(store: StoreProfile):
        try:
            store.profile_photo_url = None
            store.save()
            return store
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to delete profile photo url: {e}"
            )

    @staticmethod
    def delete_profile_photo_from_s3(store: StoreProfile):
        try:
            key = get_store_profile_photo_key(store)
            S3Service().delete_image(key)
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to delete profile photo from s3: {e}"
            )

    @staticmethod
    @transaction.atomic
    def initialize_store_defaults(store: StoreProfile):
        StoreService.initialize_default_categories(store)
        StoreService.initialize_default_conditions(store)
        StoreService.initialize_store_notifications(store)

    @staticmethod
    @transaction.atomic
    def initialize_default_categories(store_profile: StoreProfile):
        try:
            item_categories = ItemCategory.objects.all()
            for category in item_categories:
                StoreItemCategory.objects.create(store=store_profile, category=category)
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to initialize default categories: {e}"
            )

    @staticmethod
    @transaction.atomic
    def initialize_default_conditions(store_profile: StoreProfile):
        try:
            item_conditions = ItemCondition.objects.all()
            for condition in item_conditions:
                StoreItemCondition.objects.create(
                    store=store_profile, condition=condition
                )
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to initialize default conditions: {e}"
            )

    @staticmethod
    def initialize_store_notifications(store_profile: StoreProfile):
        try:
            StoreNotificationPreferences.objects.create(store=store_profile)
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to initialize store notifications: {e}"
            )


class StoreValidationService:
    @staticmethod
    def validate_stock_limit(store: StoreProfile, stock_limit: int):
        if stock_limit < store.active_listings_count:
            raise serializers.ValidationError(
                "Stock limit cannot be less than the number of active listings."
            )

    @staticmethod
    def validate_store_pin(store: StoreProfile, pin: str):
        if not store.validate_pin(pin):
            raise serializers.ValidationError("Invalid PIN.")


class StoreItemCategoryService:
    @staticmethod
    def get_store_categories(store: StoreProfile):
        return store.preferred_categories.all()

    @staticmethod
    @transaction.atomic
    def update_store_categories(store: StoreProfile, category_ids: list[int]):
        try:
            categories = ItemCategory.objects.filter(id__in=category_ids)
            store.preferred_categories.all().delete()
            for category in categories:
                StoreItemCategory.objects.create(store=store, category=category)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update store categories: {e}")
