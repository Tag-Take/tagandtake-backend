from rest_framework import serializers
from apps.items.models import Item, ItemCategory, ItemCondition, ItemImages


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "description",
            "size",
            "brand",
            "price",
            "categories_list",
            "condition",
            "status",
            "all_images",
        ]
        read_only_fields = ["main_image", "all_images", "categories_list", "status"]


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ["id", "name", "description"]


class ItemConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCondition
        fields = ["id", "condition", "description"]


class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImages
        fields = ["image_url", "order"]
