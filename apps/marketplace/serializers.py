from rest_framework import serializers

from apps.marketplace.models import ItemListing, RecallReason, RecalledItemListing
from apps.items.serializers import ItemRetrieveUpdateDeleteSerializer
from apps.marketplace.services.listing_services import ListingHandler


class CreateListingSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(write_only=True)
    tag_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemListing
        fields = ["id", "item_id", "tag_id"]

    def create(self, validated_data):
        item_id = validated_data.pop("item_id")
        tag_id = validated_data.pop("tag_id")
        try:
            listing = ListingHandler.create_listing(item_id=item_id, tag_id=tag_id)
            return listing
        except Exception as e:
            raise serializers.ValidationError(str(e))


class ListingSerializer(serializers.ModelSerializer):
    item_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    transaction_fee = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    listing_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    store_commission_amount = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    member_earnings = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    item_details = ItemRetrieveUpdateDeleteSerializer(read_only=True)

    class Meta:
        model = ItemListing
        fields = [
            "id",
            "item",
            "tag",
            "store_commission",
            "min_listing_days",
            "item_price",
            "transaction_fee",
            "listing_price",
            "store_commission_amount",
            "member_earnings",
            "item_details",
            "created_at",
            "updated_at",
        ]


class RecallReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecallReason
        fields = "__all__"


class RecallListingSerializer(serializers.ModelSerializer):
    item_price = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    transaction_fee = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    store_commission_amount = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    member_earnings = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    item_details = ItemRetrieveUpdateDeleteSerializer(read_only=True)
    reason = RecallReasonSerializer()

    class Meta:
        model = RecalledItemListing
        fields = [
            "id",
            "item",
            "tag",
            "store_commission",
            "min_listing_days",
            "reason",
            "item_price",
            "transaction_fee",
            "store_commission_amount",
            "member_earnings",
            "item_details",
            "created_at",
            "updated_at",
        ]
