from rest_framework import serializers

from apps.marketplace.models import ItemListing, RecallReason, RecalledItemListing
from apps.items.serializers import ItemRetrieveUpdateDeleteSerializer
from apps.marketplace.services.listing_services import ItemListingHandler
from apps.common.constants import *


class CreateListingSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(write_only=True)
    tag_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemListing
        fields = [ID, ITEM_ID, TAG_ID]

    def create(self, validated_data):
        item_id = validated_data.pop(ITEM_ID)
        tag_id = validated_data.pop(TAG_ID)
        try:
            listing = ItemListingHandler.create_listing(item_id=item_id, tag_id=tag_id)
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
            ID,
            ITEM,
            TAG,
            STORE_COMMISSION,
            MIN_LISTING_DAYS,
            ITEM_PRICE,
            TRANSACTION_FEE,
            LISTING_PRICE,
            STORE_COMMISSION_AMOUNT,
            MEMBER_EARNINGS,
            ITEM_DETAILS,
            CREATED_AT,
            UPDATED_AT,
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
            ID,
            ITEM,
            TAG,
            STORE_COMMISSION,
            MIN_LISTING_DAYS,
            RECALL_REASON,
            ITEM_PRICE,
            TRANSACTION_FEE,
            LISTING_PRICE,
            MEMBER_EARNINGS,
            ITEM_DETAILS,
            CREATED_AT,
            UPDATED_AT,
        ]
