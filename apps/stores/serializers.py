from rest_framework import serializers

from apps.stores.models import (
    StoreProfile,
    StoreAddress,
    StoreOpeningHours,
    StoreItemCategory,
    StoreItemCondition,
    StoreNotificationPreferences,
)
from apps.items.models import ItemCategory, ItemCondition
from apps.items.serializers import ItemCategorySerializer, ItemConditionSerializer
from apps.common.constants import *
from apps.stores.services.store_services import StoreService


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
    store_address = StoreAddressSerializer(required=False)

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
            STORE_ADDRESS,
            CREATED_AT,
            UPDATED_AT,
        ]
        read_only_fields = [
            USER,
            CREATED_AT,
            UPDATED_AT,
            OPENING_HOURS,
            STORE_ADDRESS,
            ACTIVE_LISTINGS_COUNT,
            ACCEPTING_LISTINGS,
            PROFILE_PHOTO_URL,
            REMAINING_STOCK,
        ]


class StoreItemCategorySerializer(serializers.ModelSerializer):
    category = ItemCategorySerializer()

    class Meta:
        model = StoreItemCategory
        fields = [ID, CATEGORY]


class StoreItemCategoryBulkSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=ItemCategory.objects.all())
    )

    class Meta:
        model = StoreItemCategory
        fields = [ID, CATEGORIES]

    def create(self, validated_data):
        store = self.context[STORE]
        categories = validated_data[CATEGORIES]
        store_item_categories = [
            StoreItemCategory(store=store, category=category) for category in categories
        ]
        return StoreItemCategory.objects.bulk_create(store_item_categories)


class StoreItemConditionSerializer(serializers.ModelSerializer):
    condition = ItemConditionSerializer()

    class Meta:
        model = StoreItemCondition
        fields = [ID, CONDITION]


class StoreItemConditionUpdateSerializer(serializers.Serializer):
    conditions = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=ItemCondition.objects.all())
    )

    class Meta:
        model = StoreItemCondition
        fields = [ID, CONDITIONS]

    def create(self, validated_data):
        store = self.context[STORE]
        conditions = validated_data[CONDITIONS]
        store_item_categories = [
            StoreItemCondition(store=store, condition=condition)
            for condition in conditions
        ]
        return StoreItemCondition.objects.bulk_create(store_item_categories)


class StoreNotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreNotificationPreferences
        fields = [NEW_LISTING_NOTIFICATIONS, SALE_NOTIFICATIONS]
        

class StoreProfileImageSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(write_only=True)
    profile_photo_url = serializers.URLField(read_only=True)

    class Meta:
        model = StoreProfile
        fields = [PROFILE_PHOTO, PROFILE_PHOTO_URL]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context['request'].method == 'POST':
            self.fields[PROFILE_PHOTO].required = True
        else:
            self.fields[PROFILE_PHOTO].required = False

    def update(self, instance, validated_data):
        profile_photo = validated_data.get(PROFILE_PHOTO)
        if profile_photo:
            instance = StoreService.update_store_profile_photo(instance, profile_photo)
        elif self.context['request'].method == 'DELETE':
            instance = StoreService.delete_store_profile_photo(instance)
        return instance
