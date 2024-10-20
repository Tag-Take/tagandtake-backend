from django.db import transaction

from rest_framework import serializers

from apps.items.models import Item, ItemCategory, ItemCondition, ItemImages
from apps.items.services import ItemService, ItemValidationService, ItemImageService
from apps.common.constants import *


class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImages
        fields = [IMAGE_URL, ORDER]


class ItemCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    images = ItemImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [
            ID,
            NAME,
            DESCRIPTION,
            SIZE,
            BRAND,
            PRICE,
            CONDITION,
            CATEGORY,
            IMAGE,
            IMAGES,
        ]

    def create(self, validated_data: dict):
        request = self.context.get(REQUEST)
        image = validated_data.pop(IMAGE)
        member = request.user.member

        try:
            with transaction.atomic():
                item = ItemService.create_item(validated_data, member)
                ItemImageService.create_and_upload_item_image(item, image)
                return item
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create item: {e}")


class ItemRetrieveUpdateDeleteSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    images = ItemImagesSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    category_details = serializers.SerializerMethodField()
    condition_details = serializers.SerializerMethodField()
    tag_id = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            ID,
            NAME,
            DESCRIPTION,
            SIZE,
            BRAND,
            PRICE,
            CONDITION,
            CATEGORY,
            STATUS,
            TAG_ID,
            IMAGE,
            IMAGES,
            MAIN_IMAGE,
            CATEGORY_DETAILS,
            CONDITION_DETAILS,
        ]
        read_only_fields = [STATUS, CREATED_AT, UPDATED_AT]

    def update(self, item: Item, validated_data: dict):
        image = validated_data.pop(IMAGE, None)

        with transaction.atomic():
            if validated_data:
                item = ItemService.update_item(item, validated_data)
            if image:
                ItemImageService.update_and_replace_item_image(item, image)

        return item

    def destroy(self, item: Item):
        with transaction.atomic():
            ItemImageService.delete_item_images(item)
            ItemService.delete_item(item)

    def get_main_image(self, item: Item):
        return item.main_image

    def get_category_details(self, item: Item):
        return ItemCategorySerializer(item.category).data

    def get_condition_details(self, item: Item):
        return ItemConditionSerializer(item.condition).data
    
    def get_tag_id(self, item: Item):
        return item.tag_id


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = [ID, NAME, DESCRIPTION]


class ItemConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCondition
        fields = [ID, CONDITION, DESCRIPTION]
