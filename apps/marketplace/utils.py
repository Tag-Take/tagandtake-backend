from rest_framework import serializers
from apps.marketplace.models import Listing
from apps.stores.models import Tag


def get_listing_by_tag_id(tag_id: int, listing_model=Listing):
    try:
        tag = Tag.objects.get(id=tag_id)
        listing = listing_model.objects.get(tag=tag)
        return listing
    except Tag.DoesNotExist:
        raise serializers.ValidationError("Tag not found")
    except listing_model.DoesNotExist:
        raise serializers.ValidationError(f"{listing_model.__name__} not found for the provided tag ID")

def get_listing_by_item_id(item_id: int, listing_model=Listing):
    try:
        listing = listing_model.objects.get(item_id=item_id)
        return listing
    except listing_model.DoesNotExist:
        raise serializers.ValidationError(f"{listing_model.__name__} not found for the provided item ID")
    