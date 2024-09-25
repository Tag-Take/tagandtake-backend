from django.db import transaction

from rest_framework import serializers

from apps.common.s3.s3_utils import S3Service
from apps.common.s3.s3_config import get_store_profile_photo_key
from apps.accounts.models import User
from apps.items.models import ItemCategory, ItemCondition
from apps.stores.models import (
    StoreItemCategorie,
    StoreItemConditions,
    StoreAddress,
    StoreOpeningHours,
    StoreNotificationPreferences,
)
from apps.stores.models import StoreProfile
from apps.common.constants import ID


class StoreService:
    @staticmethod
    def get_store(store_id: int):
        try:
            return StoreProfile.objects.get(id=store_id)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError("Store does not exist.")
        
    @staticmethod
    def get_store_by_user(user: User):
        try:
            return StoreProfile.objects.get(user=user)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError("Store does not exist.")

    @staticmethod
    def get_store_by_id_and_user(store_id: int, user: User):
        try:
            return StoreProfile.objects.get(id=store_id, user=user)
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
    def update_store_profile(store: StoreProfile, store_data: dict):
        try:
            for attr, value in store_data.items():
                setattr(store, attr, value)
            store.save()
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update store profile: {e}")

    @staticmethod
    def update_store_address(store: StoreProfile, address_data: dict):
        try:
            StoreAddress.objects.update_or_create(store=store, defaults=address_data)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update store address: {e}")

    @staticmethod
    @transaction.atomic
    def update_store_opening_hours(store: StoreProfile, opening_hours_data: dict):
        store.opening_hours.all().delete()
        try:
            for day_opening_hours in opening_hours_data:
                StoreOpeningHours.objects.create(store=store, **day_opening_hours)
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to update store opening hours: {e}"
            )
        
    @staticmethod
    def upload_store_profile_photo(store: StoreProfile, file):
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
            raise serializers.ValidationError(f"Failed to delete profile photo url: {e}")
        
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
                StoreItemCategorie.objects.create(
                    store=store_profile, category=category
                )
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
                StoreItemConditions.objects.create(
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
                StoreItemCategorie.objects.create(store=store, category=category)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update store categories: {e}")


class StoreItemCategoryValidationService:
    @staticmethod
    def validate_category_ids(category_ids: list[int]):
        if not category_ids:
            raise serializers.ValidationError(
                "You must provide at least one category ID."
            )
        categories = ItemCategory.objects.filter(id__in=category_ids)
        invalid_ids = set(category_ids) - set(categories.values_list(ID, flat=True))
        if invalid_ids:
            raise serializers.ValidationError(
                f"The following category IDs are invalid: {', '.join(map(str, invalid_ids))}"
            )


class StoreItemConditionService:
    @staticmethod
    def get_store_conditions(store: StoreProfile):
        return store.preferred_conditions.all()

    @staticmethod
    def update_store_conditions(store: StoreProfile, condition_ids: list[int]):
        try:
            conditions = ItemCondition.objects.filter(id__in=condition_ids)
            store.preferred_conditions.all().delete()
            for condition in conditions:
                StoreItemConditions.objects.create(store=store, condition=condition)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update store conditions: {e}")


class StoreItemConditionValidationService:
    @staticmethod
    def validate_condition_ids(condition_ids: list[int]):
        if not condition_ids:
            raise serializers.ValidationError(
                "You must provide at least one condition ID."
            )
        conditions = ItemCondition.objects.filter(id__in=condition_ids)
        invalid_ids = set(condition_ids) - set(conditions.values_list(ID, flat=True))
        if invalid_ids:
            raise serializers.ValidationError(
                f"The following condition IDs are invalid: {', '.join(map(str, invalid_ids))}"
            )