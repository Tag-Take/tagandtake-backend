from rest_framework import serializers
from apps.items.models import Item, ItemCategory, ItemCondition, ItemImages
from apps.common.s3.utils import S3ImageHandler
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
            'name', 'description', 'size', 'brand', 'price', 'condition',
            'category', 'image','images'
        ]

    def validate(self, data):
        category = data.get('category')
        valid_category = ItemCategory.objects.filter(id=category.id).exists()
        if not valid_category:
            raise serializers.ValidationError("Invalid category ID.")
        
        condition = data.get('condition')
        valid_condition = ItemCondition.objects.filter(id=condition.id).exists()
        if not valid_condition:
            raise serializers.ValidationError("Invalid condition ID.")

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        image = validated_data.pop('image')
        order = 0

        item = Item.objects.create(owner=request.user, **validated_data, status='available')

        s3_handler = S3ImageHandler()

        folder_name = get_item_images_folder(item.id)
        key = f"{folder_name}/{FILE_NAMES['item_image']}_{order}.{IMAGE_FILE_TYPE}"
        image_url = s3_handler.upload_image(image, key)

        ItemImages.objects.create(item=item, image_url=image_url, order=order)

        return item
    


class ItemRetrieveUpdateDeleteSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)
    images = ItemImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = [
            'name', 'description', 'size', 'brand', 'price', 'condition',
            'category', 'image', 'images'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate(self, data):
        category = data.get('category')
        valid_category = ItemCategory.objects.filter(id=category.id).exists()
        if not valid_category:
            raise serializers.ValidationError("Invalid category ID.")
        
        condition = data.get('condition')
        valid_condition = ItemCondition.objects.filter(id=condition.id).exists()
        if not valid_condition:
            raise serializers.ValidationError("Invalid condition ID.")

        return data
    
    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if image:
            s3_handler = S3ImageHandler()
            order = 0  

            try:
                folder_name = get_item_images_folder(instance.id)
                key = f"{folder_name}/{FILE_NAMES['item_image']}_{order}.{IMAGE_FILE_TYPE}"
                image_url = s3_handler.upload_image(image, key)

                item_image, created = ItemImages.objects.update_or_create(
                    item=instance,
                    order=order,
                    defaults={'image_url': image_url}
                )
            except Exception as e:
                raise serializers.ValidationError(f"Failed to upload image: {e}")

        instance.save()
        return instance

    def destroy(self, instance):
        s3_handler = S3ImageHandler()
        folder_name = get_item_images_folder(instance.id)

        try:
            for image in instance.images.all():
                key = f"{folder_name}/{FILE_NAMES['item_image']}_{image.order}.{IMAGE_FILE_TYPE}"
                s3_handler.delete_image(key)

            instance.delete()
        except Exception as e:
            raise serializers.ValidationError(f"Failed to delete item: {e}")


class MemberItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price', 'main_image']

    def get_main_image(self, obj):
        return


class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ["id", "name", "description"]


class ItemConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCondition
        fields = ["id", "condition", "description"]



