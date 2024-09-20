from django.db import transaction

from rest_framework import serializers

from apps.items.models import Item, ItemCategory, ItemCondition, ItemImages
from apps.common.s3.s3_utils import S3ImageHandler
from apps.common.s3.s3_config import get_item_images_folder, IMAGE_FILE_TYPE, FILE_NAMES
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

    def validate(self, data: dict):
        category = data.get(CATEGORY)
        valid_category = ItemCategory.objects.filter(id=category.id).exists()
        if not valid_category:
            raise serializers.ValidationError("Invalid category ID.")

        condition = data.get(CONDITION)
        valid_condition = ItemCondition.objects.filter(id=condition.id).exists()
        if not valid_condition:
            raise serializers.ValidationError("Invalid condition ID.")

        return data

    def create(self, validated_data: dict):
        request = self.context.get(REQUEST)
        image = validated_data.pop(IMAGE)
        member = request.user.member
        order = 0

        try:
            with transaction.atomic():
                item = Item.objects.create(
                    owner=member, **validated_data, status=Item.Statuses.AVAILABLE
                )

                folder_name = get_item_images_folder(item.id)
                key = (
                    f"{folder_name}/{FILE_NAMES[ITEM_IMAGE]}_{order}.{IMAGE_FILE_TYPE}"
                )
                image_url = S3ImageHandler().upload_image(image, key)

                ItemImages.objects.create(item=item, image_url=image_url, order=order)

                return item
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create item: {e}")


class ItemRetrieveUpdateDeleteSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    images = ItemImagesSerializer(many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    category_details = serializers.SerializerMethodField()
    condition_details = serializers.SerializerMethodField()

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
            IMAGE,
            IMAGES,
            MAIN_IMAGE,
            CATEGORY_DETAILS,
            CONDITION_DETAILS,
        ]
        read_only_fields = [STATUS, CREATED_AT, UPDATED_AT]

    def validate(self, data: dict):
        category = data.get(CATEGORY)
        valid_category = ItemCategory.objects.filter(id=category.id).exists()
        if not valid_category:
            raise serializers.ValidationError("Invalid category ID.")

        condition = data.get(CONDITION)
        valid_condition = ItemCondition.objects.filter(id=condition.id).exists()
        if not valid_condition:
            raise serializers.ValidationError("Invalid condition ID.")

        return data

    def update(self, item: Item, validated_data: dict):
        image = validated_data.pop(IMAGE, None)

        for key, value in validated_data.items():
            setattr(item, key, value)

        if image:
            s3_handler = S3ImageHandler()
            order = 0

            try:
                folder_name = get_item_images_folder(item.id)
                key = (
                    f"{folder_name}/{FILE_NAMES[ITEM_IMAGE]}_{order}.{IMAGE_FILE_TYPE}"
                )
                image_url = s3_handler.upload_image(image, key)

                item_image, created = ItemImages.objects.update_or_create(
                    item=item, order=order, defaults={IMAGE_URL: image_url}
                )
            except Exception as e:
                raise serializers.ValidationError(f"Failed to upload image: {e}")

        item.save()
        return item

    def destroy(self, item: Item):
        s3_handler = S3ImageHandler()
        folder_name = get_item_images_folder(item.id)

        try:
            for image in item.images.all():
                key = f"{folder_name}/{FILE_NAMES[ITEM_IMAGE]}_{image.order}.{IMAGE_FILE_TYPE}"
                s3_handler.delete_image(key)

            item.delete()
        except Exception as e:
            raise serializers.ValidationError(f"Failed to delete item: {e}")

    def get_main_image(self, item: Item):
        return item.main_image

    def get_category_details(self, item: Item):
        category = item.category
        return ItemCategorySerializer(category).data

    def get_condition_details(self, item: Item):
        condition = item.condition
        return ItemConditionSerializer(condition).data


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = [ID, NAME, DESCRIPTION]


class ItemConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCondition
        fields = [ID, CONDITION, DESCRIPTION]
