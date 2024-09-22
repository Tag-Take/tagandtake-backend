from django.db import transaction

from rest_framework import serializers

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


class StoreService:
    @staticmethod
    def get_store(store_id: int):
        try:
            return StoreProfile.objects.get(id=store_id)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError("Store does not exist.")

    @staticmethod
    def create_store_profile(user: User, store_profile_data: dict):
        return StoreProfile.objects.create(user=user, **store_profile_data)

    @staticmethod
    def create_store_address(store: StoreProfile, address_data: dict):
        return StoreAddress.objects.create(store=store, **address_data)

    @staticmethod
    def create_store_opening_hours(store: StoreProfile, opening_hours_data: dict):
        return StoreOpeningHours.objects.create(store=store, **opening_hours_data)

    @staticmethod
    def initialize_store_defaults(store: StoreProfile):
        StoreService.initialize_default_categories(store)
        StoreService.initialize_default_conditions(store)
        StoreService.initialize_store_notifications(store)

    @staticmethod
    @transaction.atomic
    def initialize_default_categories(store_profile: StoreProfile):
        item_categories = ItemCategory.objects.all()
        for category in item_categories:
            StoreItemCategorie.objects.create(store=store_profile, category=category)

    @staticmethod
    @transaction.atomic
    def initialize_default_conditions(store_profile: StoreProfile):
        item_conditions = ItemCondition.objects.all()
        for condition in item_conditions:
            StoreItemConditions.objects.create(store=store_profile, condition=condition)

    @staticmethod
    def initialize_store_notifications(store_profile: StoreProfile):
        StoreNotificationPreferences.objects.create(store=store_profile)
