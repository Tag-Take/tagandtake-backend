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
from apps.items.serializers import ItemCategorySerializer, ItemConditionSerializer
from apps.common.constants import *
from apps.stores.services.store_services import (
    StoreService,
    StoreValidationService,
    StoreItemCategoryService,
    StoreItemCategoryValidationService,
    StoreItemConditionService,
    StoreItemConditionValidationService,
)


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
        stock_limit = data.get(STOCK_LIMIT)
        if stock_limit and isinstance(self.instance, StoreProfile):
            StoreValidationService.validate_stock_limit(self.instance, stock_limit)
        return data

    def update(self, store: StoreProfile, validated_data: dict):
        address_data = validated_data.pop(ADDRESS, None)
        opening_hours_data = validated_data.pop(OPENING_HOURS, None)

        StoreService.update_store_profile(store, validated_data)
        if address_data:
            StoreService.update_store_address(store, address_data)
        if opening_hours_data:
            StoreService.update_store_opening_hours(store, opening_hours_data)

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
        pin = data.get(PIN)
        category_ids = data.get(CATEGORIES)

        store = StoreService.get_store_by_id_and_user(store_id, user)
        StoreItemCategoryValidationService.validate_category_ids(category_ids)

        data[STORE] = store
        return data

    def update_categories(self):
        store: StoreProfile = self.validated_data[STORE]
        categories = self.validated_data[CATEGORIES]

        StoreItemCategoryService.update_store_categories(store, categories)


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
        pin = data.get(PIN)
        condition_ids = data.get(CONDITIONS)

        store = StoreService.get_store_by_id_and_user(store_id, user)
        StoreValidationService.validate_store_pin(store, pin)
        StoreItemConditionValidationService.validate_condition_ids(condition_ids)

        data[STORE] = store
        return data

    def update_conditions(self):
        store = self.validated_data[STORE]
        conditions = self.validated_data[CONDITIONS]

        StoreItemConditionService.update_store_conditions(store, conditions)


class StoreNotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreNotificationPreferences
        fields = [NEW_LISTING_NOTIFICATIONS, SALE_NOTIFICATIONS]


class StoreProfileImageUploadSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()
    pin = serializers.CharField(max_length=4)

    def validate(self, attrs: dict):
        request: Request = self.context.get(REQUEST)
        pin = attrs.get(PIN)

        store = StoreService.get_store_by_user(request.user)
        StoreValidationService.validate_store_pin(store, pin)

        attrs[STORE] = store
        return attrs

    def save(self):
        store: StoreProfile = self.validated_data[STORE]
        file = self.validated_data[PROFILE_PHOTO]

        store = StoreService.upload_store_profile_photo(store, file)

        return store


class StoreProfileImageDeleteSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=4)

    def validate(self, attrs: dict):
        request: Request = self.context.get(REQUEST)
        pin = attrs.get(PIN)

        store = StoreService.get_store_by_user(request.user)
        StoreValidationService.validate_store_pin(store, pin)

        attrs[STORE] = store
        return attrs

    def save(self):
        store: StoreProfile = self.validated_data[STORE]

        store = StoreService.delete_store_profile_photo(store)

        return store
