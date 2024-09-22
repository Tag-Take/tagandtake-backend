from rest_framework import serializers
from rest_framework import serializers

from apps.items.models import Item, ItemImages
from apps.common.s3.s3_utils import S3ImageHandler
from apps.common.s3.s3_config import get_item_image_key
from apps.common.constants import *


class ItemService:
    @staticmethod
    def get_item(item_id: int):
        try:
            return Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Item does not exist.")

    @staticmethod
    def create_item(item_data: dict, member):
        try:
            item = Item.objects.create(owner=member, **item_data)
            return item
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create item: {e}")
        
    @staticmethod
    def update_item(item: Item, validated_data: dict):
        try:
            for key, value in validated_data.items():
                setattr(item, key, value)
            item.save()
            return item
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update item attributes: {e}")


    def delete_item(item: Item):
        try:
            item.delete()
        except Exception as e:
            raise serializers.ValidationError(f"Failed to delete item: {e}")

    @staticmethod
    def list_item(item: Item):
        item.status = Item.Statuses.LISTED
        item.save()

    @staticmethod
    def delist_item(item: Item):
        item.status = Item.Statuses.AVAILABLE
        item.save()

    @staticmethod
    def recall_item(item: Item):
        item.status = Item.Statuses.RECALLED
        item.save()

    @staticmethod
    def collect_item(item: Item):
        item.status = Item.Statuses.AVAILABLE
        item.save()

    @staticmethod
    def purchase_item(item: Item):
        item.status = Item.Statuses.SOLD
        item.save()

    @staticmethod
    def abandon_item(item: Item):
        item.status = Item.Statuses.ABANDONED
        item.save()


class ItemValidationService:
    @staticmethod
    def validate_item_availability(item: Item):
        if item.status != Item.Statuses.AVAILABLE:
            raise serializers.ValidationError(
                f"Item is not available for listing. It is currently {item.status}."
            )
        

class ItemImageService:

    @staticmethod
    def create_item_image(item: Item, image_url: str, order = 0):
        try:
            ItemImages.objects.create(item=item, image_url=image_url, order=order)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create item images: {e}")

    @staticmethod
    def update_item_image(item: Item, image_url: str, order=0):
        try:
            item_image, created = ItemImages.objects.update_or_create(
                item=item, order=order, defaults={IMAGE_URL: image_url}
            )
            return item_image
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create item images: {e}")

    @staticmethod
    def create_and_upload_item_image(item: Item, image, order=0):
        try:
            key = get_item_image_key(item, order)
            image_url = S3ImageHandler().upload_image(image, key)
            ItemImageService.create_item_image(item, image_url, order)
            return image_url
        except Exception as e:
            raise serializers.ValidationError(f"Failed to upload image: {e}")

    @staticmethod
    def update_and_replace_item_image(item: Item, image, order=0):
        try:
            key = get_item_image_key(item, order)
            image_url = S3ImageHandler().upload_image(image, key)
            ItemImageService.update_item_image(item, image_url, order)
            return image_url
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update image: {e}")

    @staticmethod
    def delete_item_images(item: Item):
        try:
            for image in item.images.all():
                key = get_item_image_key(item, image.order)
                S3ImageHandler().delete_image(key)

            ItemImages.objects.filter(item=item).delete()
        except Exception as e:
            raise serializers.ValidationError(f"Failed to delete item images: {e}")


