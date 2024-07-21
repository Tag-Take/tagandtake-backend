from rest_framework import serializers
from apps.items.models import ItemCategory, ItemCondition


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ["id", "name", "description"]


class ItemConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCondition
        fields = ["id", "condition", "description"]
