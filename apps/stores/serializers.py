from rest_framework import serializers
from rest_framework.request import Request

from apps.accounts.models import User
from apps.stores.models import (
    StoreProfile,
    StoreAddress,
    StoreOpeningHours,
    StoreItemCategorie,
    StoreItemConditions,
    StoreNotificationPreferences,
)
from apps.items.models import ItemCategory, ItemCondition
from apps.items.serializers import ItemCategorySerializer, ItemConditionSerializer
from apps.common.s3.s3_utils import S3Service
from apps.common.s3.s3_config import get_store_profile_photo_key
from apps.common.constants import *


class StoreAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreAddress
        fields = [
            STREET_ADDRESS,
            CITY,
            STATE,
            POSTAL_CODE,
            COUNTRY,
            LATITUDE,
            LONGITUDE,
        ]


class StoreOpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreOpeningHours
        fields = [
            DAY_OF_WEEK,
            OPENING_TIME,
            CLOSING_TIME,
            TIMEZONE,
            IS_CLOSED,
        ]


class StoreProfileSerializer(serializers.ModelSerializer):
    opening_hours = StoreOpeningHoursSerializer(many=True, required=False)
    address = StoreAddressSerializer(required=False)

    class Meta:
        model = StoreProfile
        fields = [
            USER,
            STORE_NAME,
            PHONE,
            STORE_BIO,
            PROFILE_PHOTO_URL,
            GOOGLE_PROFILE_URL,
            WEBSITE_URL,
            INSTAGRAM_URL,
            COMMISSION,
            STOCK_LIMIT,
            ACTIVE_LISTINGS_COUNT,
            REMAINING_STOCK,
            MIN_LISTING_DAYS,
            MIN_PRICE,
            OPENING_HOURS,
            ADDRESS,
            CREATED_AT,
            UPDATED_AT,
        ]
        read_only_fields = [
            USER,
            CREATED_AT,
            UPDATED_AT,
            OPENING_HOURS,
            ADDRESS,
            ACTIVE_LISTINGS_COUNT,
            ACCEPTING_LISTINGS,
            PROFILE_PHOTO_URL,
            REMAINING_STOCK,
        ]

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", [])

        super().__init__(*args, **kwargs)

        for field in exclude:
            self.fields.pop(field, None)

    def validate(self, data: dict):
        store: StoreProfile = self.instance
        if store is None:
            return data

        stock_limit = data.get(STOCK_LIMIT, store.stock_limit)
        if stock_limit is not None and stock_limit < store.active_listings_count:
            raise serializers.ValidationError(
                {
                    "stock_limit": "Stock limit cannot be less than the number of active tags."
                }
            )
        return data

    def update(self, store: StoreProfile, validated_data: dict):
        address_data = validated_data.pop(ADDRESS, None)
        opening_hours_data = validated_data.pop(OPENING_HOURS, None)

        for attr, value in validated_data.items():
            setattr(store, attr, value)
        store.save()

        if address_data:
            StoreAddress.objects.update_or_create(store=store, defaults=address_data)

        if opening_hours_data:
            store.opening_hours.all().delete()
            for day_opening_hours in opening_hours_data:
                StoreOpeningHours.objects.create(store=store, **day_opening_hours)

        return store


class StoreItemCategorySerializer(serializers.ModelSerializer):
    category = ItemCategorySerializer()

    class Meta:
        model = StoreItemCategorie
        fields = [ID, CATEGORY]


class StoreItemCategoryUpdateSerializer(serializers.Serializer):
    pin = serializers.CharField(write_only=True)
    categories = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    def validate(self, data: dict):
        store_id = self.context[STORE_ID]
        user: User = self.context[REQUEST].user

        try:
            store: StoreProfile = StoreProfile.objects.get(id=store_id, user=user)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError(
                "Store not found or you do not have permission."
            )

        if not store.validate_pin(data[PIN]):
            raise serializers.ValidationError("Invalid PIN.")

        data[STORE] = store

        category_ids: list[int] = data[CATEGORIES]
        if not category_ids:
            raise serializers.ValidationError(
                "You must provide at least one category ID."
            )

        categories: list[ItemCategory] = ItemCategory.objects.filter(
            id__in=category_ids
        )
        invalid_ids = set(category_ids) - set(categories.values_list(ID, flat=True))

        if invalid_ids:
            raise serializers.ValidationError(
                f"The following category IDs are invalid: {', '.join(map(str, invalid_ids))}"
            )

        data[CATEGORIES] = categories
        return data

    def update_categories(self):
        store: StoreProfile = self.validated_data[STORE]
        categories = self.validated_data[CATEGORIES]

        StoreItemCategorie.objects.filter(store=store).delete()
        for category in categories:
            StoreItemCategorie.objects.create(store=store, category=category)


class StoreItemConditionSerializer(serializers.ModelSerializer):
    condition = ItemConditionSerializer()

    class Meta:
        model = StoreItemConditions
        fields = [ID, CONDITION]


class StoreItemConditionUpdateSerializer(serializers.Serializer):
    pin = serializers.CharField(write_only=True)
    conditions = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    def validate(self, data: dict):
        store_id = self.context[STORE_ID]
        user = self.context[REQUEST].user

        try:
            store = StoreProfile.objects.get(id=store_id, user=user)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError(
                "Store not found or you do not have permission."
            )

        if not store.validate_pin(data[PIN]):
            raise serializers.ValidationError("Invalid PIN.")

        data[STORE] = store

        condition_ids = data[CONDITIONS]
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

        data[CONDITIONS] = conditions
        return data

    def update_conditions(self):
        store = self.validated_data[STORE]
        conditions = self.validated_data[CONDITIONS]

        StoreItemConditions.objects.filter(store=store).delete()
        for condition in conditions:
            StoreItemConditions.objects.create(store=store, condition=condition)


class StoreNotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreNotificationPreferences
        fields = [NEW_LISTING_NOTIFICATIONS, SALE_NOTIFICATIONS]


class StoreProfileImageUploadSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()
    pin = serializers.CharField(max_length=4)

    def validate(self, attrs: dict):
        request: Request = self.context.get(REQUEST)
        try:
            profile = StoreProfile.objects.get(user=request.user)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError("Store profile not found.")

        pin = attrs.get(PIN)
        if not pin or not profile.validate_pin(pin):
            raise serializers.ValidationError("Invalid PIN.")

        attrs[PROFILE] = profile
        return attrs

    def save(self):
        store: StoreProfile = self.validated_data[PROFILE]
        file = self.validated_data[PROFILE_PHOTO]

        s3_handler = S3Service()
        key = get_store_profile_photo_key(store)
        try:
            image_url = s3_handler.upload_image(file, key)
            store.profile_photo_url = image_url
            store.save()
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to upload profile photo: {str(e)}"
            )

        return store


class StoreProfileImageDeleteSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=4)

    def validate(self, attrs: dict):
        request: Request = self.context.get(REQUEST)
        try:
            profile = StoreProfile.objects.get(user=request.user)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError("Store profile not found.")

        pin = attrs.get(PIN)
        if not pin or not profile.validate_pin(pin):
            raise serializers.ValidationError("Invalid PIN.")

        if not profile.profile_photo_url:
            raise serializers.ValidationError("No profile photo to delete.")

        attrs[PROFILE] = profile
        return attrs

    def save(self):
        store: StoreProfile = self.validated_data[PROFILE]
        s3_handler = S3Service()
        key = get_store_profile_photo_key(store)
        try:
            s3_handler.delete_image(key)
            store.profile_photo_url = None
            store.save()
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to delete profile photo: {str(e)}"
            )

        return store
