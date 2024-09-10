from rest_framework import serializers
from apps.items.models import Item, ItemCategory, ItemCondition, ItemImages
from apps.common.s3.s3_utils import S3ImageHandler
from apps.common.s3.s3_config import get_item_images_folder, IMAGE_FILE_TYPE, FILE_NAMES
from django.db import transaction


class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImages
        fields = ["image_url", "order"]


class ItemCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    images = ItemImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "description",
            "size",
            "brand",
            "price",
            "condition",
            "category",
            "image",
            "images",
        ]

    def validate(self, data: dict):
        category = data.get("category")
        valid_category = ItemCategory.objects.filter(id=category.id).exists()
        if not valid_category:
            raise serializers.ValidationError("Invalid category ID.")

        condition = data.get("condition")
        valid_condition = ItemCondition.objects.filter(id=condition.id).exists()
        if not valid_condition:
            raise serializers.ValidationError("Invalid condition ID.")

        return data

    def create(self, validated_data: dict):
        request = self.context.get("request")
        image = validated_data.pop("image")
        member = request.user.member
        order = 0

        try:
            with transaction.atomic():
                item = Item.objects.create(
                    owner=member, **validated_data, status="available"
                )

                folder_name = get_item_images_folder(item.id)
                key = f"{folder_name}/{FILE_NAMES['item_image']}_{order}.{IMAGE_FILE_TYPE}"
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
            "id",
            "name",
            "description",
            "size",
            "brand",
            "price",
            "condition",
            "category",
            "status",
            "image",
            "images",
            "main_image",
            "category_details",
            "condition_details",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def validate(self, data: dict):
        category = data.get("category")
        valid_category = ItemCategory.objects.filter(id=category.id).exists()
        if not valid_category:
            raise serializers.ValidationError("Invalid category ID.")

        condition = data.get("condition")
        valid_condition = ItemCondition.objects.filter(id=condition.id).exists()
        if not valid_condition:
            raise serializers.ValidationError("Invalid condition ID.")

        return data

    def update(self, item: Item, validated_data: dict):
        image = validated_data.pop("image", None)

        for key, value in validated_data.items():
            setattr(item, key, value)

        if image:
            s3_handler = S3ImageHandler()
            order = 0

            try:
                folder_name = get_item_images_folder(item.id)
                key = f"{folder_name}/{FILE_NAMES['item_image']}_{order}.{IMAGE_FILE_TYPE}"
                image_url = s3_handler.upload_image(image, key)

                item_image, created = ItemImages.objects.update_or_create(
                    item=item, order=order, defaults={"image_url": image_url}
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
                key = f"{folder_name}/{FILE_NAMES['item_image']}_{image.order}.{IMAGE_FILE_TYPE}"
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
        fields = ["id", "name", "description"]


class ItemConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCondition
        fields = ["id", "condition", "description"]
