from rest_framework import serializers
from apps.marketplace.models import Listing, Item, Tag
from apps.items.serializers import ItemRetrieveUpdateDeleteSerializer


class CreateListingSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(write_only=True)
    tag_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'item_id', 'tag_id', 'store_commission', 'min_listing_days'
        ]
        extra_kwargs = {
            'store_commission': {'required': False},
            'min_listing_days': {'required': False}
        }

    def validate(self, attrs):
        item_id = attrs.get("item_id")
        tag_id = attrs.get("tag_id")

        errors = {}

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            errors["item_id"] = "Item does not exist."
            item = None

        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            errors["tag_id"] = "Tag does not exist."
            tag = None

        if item and tag:
            if Listing.objects.filter(item=item).exists():
                errors["item_id"] = "Item is already listed."
            if Listing.objects.filter(tag=tag).exists():
                errors["tag_id"] = "Tag is already associated with another item."

        if errors:
            raise serializers.ValidationError(errors)

        attrs["item"] = item
        attrs["tag"] = tag
        return attrs

    def create(self, validated_data):
        item = validated_data.pop("item")
        tag = validated_data.pop("tag")
        store_commission = tag.store.commission
        min_listing_days = tag.store.min_listing_days

        listing = Listing.objects.create(
            item=item,
            tag=tag,
            store_commission=store_commission,
            min_listing_days=min_listing_days,
        )
        return listing

class ListingSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    transaction_fee = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    store_commission_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    member_earnings = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    item_details = ItemRetrieveUpdateDeleteSerializer(read_only=True)


    class Meta:
        model = Listing
        fields = [
            'id', 'item', 'tag', 'store_commission', 'min_listing_days', 
            'price', 'transaction_fee', 'store_commission_amount', 
            'member_earnings', 'item_details', 'created_at', 'updated_at'
        ]