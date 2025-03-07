from datetime import timedelta
from django.utils.timezone import now

from rest_framework import serializers
from rest_framework.request import Request

from apps.stores.models import Tag
from apps.marketplace.models import (
    ItemListing,
    RecalledItemListing,
    DelistedItemListing,
    SoldItemListing,
    RecallReason,
)
from apps.items.models import Item
from apps.stores.models import (
    StoreItemCategory,
    StoreItemCondition,
    StoreProfile,
    StoreOpeningHours,
)
from apps.common.constants import CONDITION, CATEGORY, PRICE
from apps.marketplace.constants import ListingRole
from apps.payments.models.transactions import ItemPaymentTransaction


COLLECTION_PERIOD_DAYS = 21


class ItemListingService:
    @staticmethod
    def get_listing(listing_id: int):
        try:
            return ItemListing.objects.get(id=listing_id)
        except ItemListing.DoesNotExist:
            raise serializers.ValidationError("Listing does not exist.")

    @staticmethod
    def get_item_listing_by_tag_id(tag_id: int, listing_model=ItemListing):
        try:
            listing = listing_model.objects.get(tag__id=tag_id)
            return listing
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag not found")
        except listing_model.DoesNotExist:
            raise serializers.ValidationError(
                f"{listing_model.__name__} not found for the provided tag ID"
            )

    @staticmethod
    def get_item_listing_by_item_id(item_id: int, listing_model=ItemListing):
        try:
            listing = listing_model.objects.get(item__id=item_id)
            return listing
        except listing_model.DoesNotExist:
            raise serializers.ValidationError(
                f"{listing_model.__name__} not found for the provided item ID"
            )

    @staticmethod
    def get_recall_reasons(reason_id: int):
        try:
            return RecallReason.objects.get(id=reason_id)
        except RecallReason.DoesNotExist:
            raise serializers.ValidationError("Invalid reason provided.")

    @staticmethod
    def get_user_listing_relation(request: Request, listing: ItemListing):
        if request.user == listing.tag.tag_group.store.user:
            return ListingRole.HOST
        elif request.user == listing.item.owner_user:
            return ListingRole.OWNER
        else:
            return ListingRole.VIEWER

    @staticmethod
    def create_listing(item: Item, tag: Tag):
        return ItemListing.objects.create(
            item=item,
            tag=tag,
            store_commission=tag.store.commission,
            min_listing_days=tag.store.min_listing_days,
        )

    @staticmethod
    def delete_listing(listing: ItemListing):
        listing.delete()

    @staticmethod
    def create_recalled_listing(listing: ItemListing, reason: RecallReason):
        collection_deadline = ItemListingService.get_collection_deadline(listing.store)
        return RecalledItemListing.objects.create(
            tag=listing.tag,
            item=listing.item,
            store_commission=listing.store_commission,
            min_listing_days=listing.min_listing_days,
            reason=reason,
            collection_deadline=collection_deadline,
        )

    @staticmethod
    def delete_recalled_listing(recalled_listing: RecalledItemListing):
        recalled_listing.delete()

    @staticmethod
    def create_delisted_listing(listing: ItemListing, reason: RecallReason):
        return DelistedItemListing.objects.create(
            tag=listing.tag,
            item=listing.item,
            store_commission=listing.store_commission,
            min_listing_days=listing.min_listing_days,
            reason=reason,
        )

    def create_sold_listing(listing: ItemListing, transaction: ItemPaymentTransaction):
        return SoldItemListing.objects.create(
            tag=listing.tag,
            item=listing.item,
            store_commission=listing.store_commission,
            min_listing_days=listing.min_listing_days,
            transaction=transaction,
        )

    @staticmethod
    def replace_listing_tag(listing: ItemListing, new_tag: Tag):
        listing.tag = new_tag
        listing.save()
        return listing

    @staticmethod
    def update_recalled_listing_collection_pin(recalled_listing: RecalledItemListing):
        recalled_listing.collection_pin = RecalledItemListing.generate_collection_pin()
        recalled_listing.save()

    @staticmethod
    def get_collection_deadline(store: StoreProfile):
        opening_hours: list[StoreOpeningHours] = list(store.opening_hours.all())

        collection_date = now() + timedelta(days=COLLECTION_PERIOD_DAYS)

        day_offset = 0
        while day_offset < 7:  # Traverse up to a full week
            check_date = collection_date + timedelta(days=day_offset)
            check_day_name = check_date.strftime("%A")

            day_opening_hours = next(
                (
                    day
                    for day in opening_hours
                    if day.day_of_week.lower() == check_day_name.lower()
                ),
                None,
            )

            if day_opening_hours and not day_opening_hours.is_closed:
                closing_time = day_opening_hours.closing_time
                collection_date = check_date.replace(
                    hour=closing_time.hour,
                    minute=closing_time.minute,
                    second=0,
                    microsecond=0,
                )
                return collection_date

            day_offset += 1

        return collection_date.replace(hour=17, minute=0, second=0, microsecond=0)


class ItemListingValidationService:
    @staticmethod
    def meets_store_requirements(item: Item, tag: Tag):
        errors = {}

        errors.update(ItemListingValidationService._validate_condition(item, tag))
        errors.update(ItemListingValidationService._validate_category(item, tag))
        errors.update(ItemListingValidationService._validate_price(item, tag))
        errors.update(
            ItemListingValidationService._validate_store_availability(tag.store)
        )

        if errors:
            raise serializers.ValidationError(errors)

    @staticmethod
    def _validate_condition(item: Item, tag: Tag):
        store_conditions = StoreItemCondition.objects.filter(store=tag.store)
        if item.condition not in [
            condition.condition for condition in store_conditions
        ]:
            return {
                CONDITION: f"'{item.condition}' does not meet store condition requirements."
            }
        return {}

    @staticmethod
    def _validate_category(item: Item, tag: Tag):
        categories = StoreItemCategory.objects.filter(store=tag.store)
        if item.category not in [category.category for category in categories]:
            return {
                CATEGORY: f"{tag.store.store_name} does not accept '{item.category}' items."
            }
        return {}

    @staticmethod
    def _validate_price(item: Item, tag: Tag):
        if item.price < tag.store.min_price:
            return {
                PRICE: f"Item price is below {tag.store.store_name}'s minimum price requirement."
            }
        return {}

    def _validate_store_availability(store: StoreProfile):
        if not store.accepting_listings:
            return {"store": "Store is not currently accepting listings."}
        return {}

    @staticmethod
    def validate_tag_availability(tag, instance=None):
        active_tag_listings = ItemListing.objects.filter(tag=tag)
        if active_tag_listings.exists():
            raise serializers.ValidationError(
                "There is already an active listing with this tag."
            )
