from rest_framework import serializers
from apps.stores.models import (
    StoreProfile, 
    StoreItemCategorie,
    StoreItemConditions, 
    StoreNotificationPreferences
    )
from apps.items.models import ItemCategory, ItemCondition
from apps.items.serializers import ItemCategorySerializer, ItemConditionSerializer


class StoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProfile
        fields = [
            "user",
            "shop_name",
            "phone",
            "store_bio",
            "google_profile_url",
            "website_url",
            "instagram_url",
            "longitude",
            "latitude",
            "commission",
            "stock_limit",
            "active_tags_count",
            "remaining_stock",
            "min_listing_days",
            "min_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "active_tags_count", "created_at", "updated_at","profile_photo_url"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StoreItemCategorySerializer(serializers.ModelSerializer):
    category = ItemCategorySerializer()

    class Meta:
        model = StoreItemCategorie
        fields = ["id", "category"]


class StoreItemCategoryUpdateSerializer(serializers.Serializer):
    pin = serializers.CharField(write_only=True)
    categories = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    def validate(self, data):
        store_id = self.context["store_id"]
        user = self.context["request"].user

        try:
            store = StoreProfile.objects.get(id=store_id, user=user)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError(
                "Store not found or you do not have permission."
            )

        if not store.validate_pin(data["pin"]):
            raise serializers.ValidationError("Invalid PIN.")

        data["store"] = store

        category_ids = data['categories']
        if not category_ids:
            raise serializers.ValidationError("You must provide at least one category ID.")

        categories = ItemCategory.objects.filter(id__in=category_ids)
        invalid_ids = set(category_ids) - set(categories.values_list('id', flat=True))

        if invalid_ids:
            raise serializers.ValidationError(f"The following category IDs are invalid: {', '.join(map(str, invalid_ids))}")

        data["categories"] = categories
        return data

    def update_categories(self):
        store = self.validated_data["store"]
        categories = self.validated_data["categories"]

        StoreItemCategorie.objects.filter(store=store).delete()
        for category in categories:
            StoreItemCategorie.objects.create(store=store, category=category)


class StoreItemConditionSerializer(serializers.ModelSerializer):
    condition = ItemConditionSerializer()

    class Meta:
        model = StoreItemConditions
        fields = ["id", "condition"]


class StoreItemConditionUpdateSerializer(serializers.Serializer):
    pin = serializers.CharField(write_only=True)
    conditions = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    def validate(self, data):
        store_id = self.context["store_id"]
        user = self.context["request"].user

        try:
            store = StoreProfile.objects.get(id=store_id, user=user)
        except StoreProfile.DoesNotExist:
            raise serializers.ValidationError(
                "Store not found or you do not have permission."
            )

        if not store.validate_pin(data["pin"]):
            raise serializers.ValidationError("Invalid PIN.")

        data["store"] = store

        condition_ids = data['conditions']
        if not condition_ids:
            raise serializers.ValidationError("You must provide at least one condition ID.")

        conditions = ItemCondition.objects.filter(id__in=condition_ids)
        invalid_ids = set(condition_ids) - set(conditions.values_list('id', flat=True))

        if invalid_ids:
            raise serializers.ValidationError(f"The following condition IDs are invalid: {', '.join(map(str, invalid_ids))}")


        data["conditions"] = conditions
        return data

    def update_conditions(self):
        store = self.validated_data["store"]
        conditions = self.validated_data["conditions"]

        StoreItemConditions.objects.filter(store=store).delete()
        for condition in conditions:
            StoreItemConditions.objects.create(store=store, condition=condition)


class StoreNotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreNotificationPreferences
        fields = ['new_listing_notifications', 'sale_notifications']