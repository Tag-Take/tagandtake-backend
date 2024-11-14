from rest_framework import serializers

from apps.marketplace.models import ItemListing, RecallReason, RecalledItemListing
from apps.items.serializers import ItemRetrieveUpdateDeleteSerializer
from apps.marketplace.services.listing_services import ItemListingValidationService
from apps.common.constants import *
from apps.items.services import ItemValidationService
from apps.stores.services.tags_services import TagService
from apps.marketplace.processors import ItemListingCreateProcessor
from apps.marketplace.services.listing_services import ItemListingService
from apps.items.serializers import ItemCreateSerializer, FlatItemSerializer
from apps.items.models import Item
from apps.stores.models import Tag


class CreateListingSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(write_only=True)
    tag_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemListing
        fields = [ID, ITEM_ID, TAG_ID]

    def validate(self, data):
        item = Item.objects.get(id=data.get(ITEM_ID))
        tag = Tag.objects.get(id=data.get(TAG_ID))
        ItemValidationService.validate_item_availability(item)
        ItemListingValidationService.validate_tag_availability(tag)
        ItemListingValidationService.meets_store_requirements(item, tag)

        data[ITEM] = item
        data[TAG] = tag
        return data

    def create(self, validated_data):
        item = validated_data.get(ITEM)
        tag = validated_data.get(TAG)
        processor = ItemListingCreateProcessor(item, tag)
        return processor.process()


class CreateItemAndListingSerializer(serializers.Serializer):
    item = FlatItemSerializer()
    tag_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        item_data = validated_data.pop(ITEM)
        item_serializer = ItemCreateSerializer(data=item_data, context=self.context)
        item_serializer.is_valid(raise_exception=True)
        item = item_serializer.save()
        listing_data = {
            ITEM_ID: item.id,
            TAG_ID: validated_data[TAG_ID],
        }
        listing_serializer = CreateListingSerializer(
            data=listing_data, context=self.context
        )
        listing_serializer.is_valid(raise_exception=True)
        listing = listing_serializer.save()

        return listing


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
    user_listing_relation = serializers.SerializerMethodField()

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
            USER_LISTING_RELATION,
        ]

    def get_user_listing_relation(self, obj):
        request = self.context.get(REQUEST)

        if isinstance(obj, ItemListing):
            return ItemListingService.get_user_listing_relation(request, obj)

        return TagService.get_user_tag_relation(request, obj)

    def to_representation(self, instance):
        if isinstance(instance, ItemListing):
            data = super().to_representation(instance)
            data[USER_LISTING_RELATION] = self.get_user_listing_relation(instance)
            data[LISTING_EXISTS] = True
            return data

        return {
            USER_LISTING_RELATION: self.get_user_listing_relation(instance),
            LISTING_EXISTS: False,
        }


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
