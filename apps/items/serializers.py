from rest_framework import serializers
from apps.items.models import Item, ItemCategory, ItemCondition, ItemImages
from apps.common.s3.utils import S3ImageHandler
from apps.common.s3.s3_config import get_item_images_folder, IMAGE_FILE_TYPE, FILE_NAMES
from django.db import transaction


class ItemImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
    order = serializers.IntegerField()


class ItemCreateSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, write_only=True)

    class Meta:
        model = Item
        fields = [
            'name', 'description', 'size', 'brand', 'price', 'condition',
            'categories_list', 'images'
        ]

    def validate(self, data):
        if 'images' not in data or len(data['images']) == 0:
            raise serializers.ValidationError("At least one image is required to create an item.")
        
        if 'categories_list' not in data or len(data.get('categories_list')) == 0:
            raise serializers.ValidationError("At least one category is required to create an item.")
        
        category_ids = data.get('categories_list')
        valid_categories = ItemCategory.objects.filter(id__in=category_ids).count()
        if valid_categories != len(category_ids):
            raise serializers.ValidationError("One or more category IDs are invalid.")
        
        condition = data.get('condition')
        valid_condition = ItemCondition.objects.filter(id=condition).exists()
        if not valid_condition:
            raise serializers.ValidationError("Invalid condition ID.")

        return data

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        categories_data = validated_data.pop('categories_list', [])

        
        with transaction.atomic():
            item = Item.objects.create(**validated_data, status='available')
            item.categories_list.set(categories_data)

            s3_handler = S3ImageHandler()
            for image_data in images_data:
                image = image_data['image']
                order = image_data['order']
                folder_name = get_item_images_folder(item.id)
                key = f"{folder_name}/{FILE_NAMES['item_image']}_{order}.{IMAGE_FILE_TYPE}"
                image_url = s3_handler.upload_image(image, key)

                ItemImages.objects.create(item=item, image_url=image_url, order=order)

            return item


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
