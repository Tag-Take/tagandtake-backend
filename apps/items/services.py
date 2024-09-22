from rest_framework import serializers

from apps.items.models import Item


class ItemService:
    @staticmethod
    def get_item(item_id: int):
        try:
            return Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Item does not exist.")

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
