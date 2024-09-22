from rest_framework import serializers

from apps.marketplace.models import ItemListing, RecallReason, RecalledItemListing
from apps.items.serializers import ItemRetrieveUpdateDeleteSerializer
from apps.marketplace.services.listing_services import ItemListingValidationService
from apps.common.constants import *
from apps.items.services import ItemService, ItemValidationService
from apps.stores.services.tags_services import TagService
from apps.marketplace.handlers import ItemListingCreateHandler


class CreateListingSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(write_only=True)
    tag_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemListing
        fields = [ID, ITEM_ID, TAG_ID]

    def validate(self, data):
        try:
            item = ItemService.get_item(data.get(ITEM_ID))
            tag = TagService.get_tag(data.get(TAG_ID))
            ItemValidationService.validate_item_availability(item)
            ItemListingValidationService.meets_store_requirements(item, tag)

            data[ITEM] = item
            data[TAG] = tag
            return data
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.detail)

    def create(self, validated_data):
        item = validated_data.get(ITEM)
        tag = validated_data.get(TAG)
        handler = ItemListingCreateHandler(item, tag)
        return handler.handle()


class ItemListingSerializer(serializers.ModelSerializer):
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


class RecallItemListingSerializer(serializers.ModelSerializer):
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
            STORE_COMMISSION_AMOUNT,
            MIN_LISTING_DAYS,
            ITEM_PRICE,
            TRANSACTION_FEE,
            LISTING_PRICE,
            MEMBER_EARNINGS,
            ITEM_DETAILS,
            CREATED_AT,
            REASON,
            UPDATED_AT,
        ]
