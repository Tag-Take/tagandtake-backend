from datetime import timedelta
from django.db import transaction
from django.utils.timezone import now
from decimal import Decimal

from rest_framework import serializers
from rest_framework.request import Request

from apps.stores.models import Tag
from apps.marketplace.models import (
    Listing,
    RecalledListing,
    DelistedListing,
    SoldListing,
    RecallReason,
)
from apps.items.models import Item
from apps.stores.models import StoreItemCategorie, StoreItemConditions
from apps.members.models import MemberProfile as Member
from apps.marketplace.services.pricing_services import (
    RECALLED_LISTING_RECURRING_FEE,
    GRACE_PERIOD_DAYS,
    RECURRING_FEE_INTERVAL_DAYS,
)
from apps.emails.services.email_senders import ListingEmailSender
from apps.marketplace.permissions import IsTagOwner
from apps.items.permissions import IsItemOwner
from apps.stores.permissions import IsStoreUser


class ListingHandler:
    def create_listing(self, item_id: int, tag_id: int):
        # TODO: create check_member_payment_details(user)
        # elegantly handle instances where member
        # hasn't added payment details - redirect to
        # add payment details
        item = self.get_item(item_id)
        tag = self.get_tag(tag_id)
        self.item_meets_store_requirements(item, tag)
        with transaction.atomic():
            listing = Listing.objects.create(
                item=item,
                tag=tag,
                store_commission=tag.store.commission,
                min_listing_days=tag.store.min_listing_days,
            )
            item.status = "Listed"
            item.save()
            ListingEmailSender.send_listing_created_email(listing)
        return listing

    def recall_listing(self, listing: Listing, reason_id: int):
        try:
            reason = self.get_recall_reasons(reason_id)
            with transaction.atomic():
                RecalledListing.objects.create(
                    tag=listing.tag,
                    item=listing.item,
                    store_commission=listing.store_commission,
                    min_listing_days=listing.min_listing_days,
                    reason=reason,
                    next_fee_charge_at=now()
                    + timedelta(days=self.get_grace_period_days()),
                )
                listing.item.status = "recalled"
                listing.item.save()
                ListingEmailSender.send_listing_recalled_email(listing, reason)
                listing.delete()
        except RecallReason.DoesNotExist:
            raise serializers.ValidationError("Invalid reason provided")

    def delist_listing(self, listing: Listing, reason_id: int):
        try:
            reason = self.get_recall_reasons(reason_id)
            with transaction.atomic():
                DelistedListing.objects.create(
                    tag=listing.tag,
                    item=listing.item,
                    store_commission=listing.store_commission,
                    min_listing_days=listing.min_listing_days,
                    reason=reason,
                )
                listing.item.status = "available"
                listing.item.save()
                ListingEmailSender().send_listing_delisted_email(listing)
                listing.delete()
        except RecallReason.DoesNotExist:
            raise serializers.ValidationError("Invalid reason provided")

    @staticmethod
    def delist_recalled_listing(recalled_listing: RecalledListing):
        with transaction.atomic():
            DelistedListing.objects.create(
                tag=recalled_listing.tag,
                item=recalled_listing.item,
                store_commission=recalled_listing.store_commission,
                min_listing_days=recalled_listing.min_listing_days,
                reason=recalled_listing.reason,
            )
            recalled_listing.item.status = "available"
            recalled_listing.item.save()
            ListingEmailSender.send_recalled_listing_collected_email(recalled_listing)
            recalled_listing.delete()

    @staticmethod
    def purchase_listing(listing: Listing, buyer: Member = None):
        if listing:
            with transaction.atomic():
                SoldListing.objects.create(
                    tag=listing.tag,
                    item=listing.item,
                    store_commission=listing.store_commission,
                    min_listing_days=listing.min_listing_days,
                    buyer=buyer,
                )
                listing.item.status = "sold"
                listing.item.save()
                ListingEmailSender.send_listing_sold_email(listing)
                listing.delete()

    def replace_listing_tag(self, listing: Listing, new_tag_id: int):
        new_tag = self.get_tag(new_tag_id)
        with transaction.atomic():
            listing.tag = new_tag
            listing.save()
            return listing

    def apply_recurring_storage_fee(self, recalled_listing: RecalledListing):
        with transaction.atomic():
            recalled_listing.fee_charged_count += 1
            recalled_listing.last_fee_charge_at = now()
            recalled_listing.last_fee_charge_amount = (
                recalled_listing.last_fee_charge_amount or Decimal("0.00")
            ) + RECALLED_LISTING_RECURRING_FEE
            recalled_listing.next_fee_charge_at = now() + timedelta(
                days=self.get_recurring_fee_interval_days()
            )
            recalled_listing.save()
            ListingEmailSender.send_storage_fee_charged_email(recalled_listing)

    @staticmethod
    def item_meets_store_requirements(item: Item, tag: Tag):
        store_conditions = StoreItemConditions.objects.filter(store=tag.store)
        categories = StoreItemCategorie.objects.filter(store=tag.store)

        errors = {}

        if item.condition not in [
            condition.condition for condition in store_conditions
        ]:
            errors["condition"] = (
                f"'{item.condition}' does not meet store condition requirements."
            )

        if item.category not in [category.category for category in categories]:
            errors["category"] = (
                f"{tag.store.store_name} does not accept '{item.category}' items."
            )

        if item.price < tag.store.min_price:
            errors["price"] = (
                f"Item price is below {tag.store.store_name}'s minimum price requirement."
            )

        if errors:
            raise serializers.ValidationError(errors)

    @staticmethod
    def get_tag(tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
            return tag
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag does not exist.")

    @staticmethod
    def get_item(item_id):
        try:
            item = Item.objects.get(id=item_id)
            if item.status != "available":
                raise serializers.ValidationError(
                    f"Item is not available for listing. Item is currelty {item.status}."
                )
            return item
        except Item.DoesNotExist:
            raise serializers.ValidationError("Item does not exist.")

    @staticmethod
    def get_recall_reasons(id):
        try:
            return RecallReason.objects.get(id=id)
        except RecallReason.DoesNotExist:
            raise serializers.ValidationError("Invalid reason provided")

    @staticmethod
    def get_grace_period_days():
        return GRACE_PERIOD_DAYS

    @staticmethod
    def get_recurring_fee_interval_days():
        return RECURRING_FEE_INTERVAL_DAYS


class RecalledListingCollectionReminderService:
    def __init__(self, recalled_listing: RecalledListing):
        self.recalled_listing = recalled_listing

    def is_time_to_remind(self):
        if (
            not now() >= self.recalled_listing.next_fee_charge_at
            and not self.recalled_listing.next_fee_charge_at.date() == now().date()
        ):
            return True

    def send_listing_collection_reminder(self):
        ListingEmailSender.send_collection_reminder_email(self.recalled_listing)

    @staticmethod
    def run_storage_fee_reminder_checks():
        # TODO: integrate store closing hours in reminder (EOD is the last collection time)
        recalled_listings = RecalledListing.objects.all()
        for recalled_listing in recalled_listings:
            service = RecalledListingCollectionReminderService(recalled_listing)
            if service.is_time_to_remind():
                service.send_listing_collection_reminder()


class RecalledListingStorageFeeService:
    def __init__(self, recalled_listing: RecalledListing):
        self.recalled_listing = recalled_listing

    def is_time_to_charge(self):
        return now() >= self.recalled_listing.next_fee_charge_at

    def apply_storage_fee(self):
        ListingHandler.apply_recurring_storage_fee(self.recalled_listing)

    @staticmethod
    def run_storage_fee_checks():
        # TODO: integrate store closing hours in fee application (EOD is the last collection time)
        recalled_listings = RecalledListing.objects.all()
        for recalled_listing in recalled_listings:
            service = RecalledListingStorageFeeService(recalled_listing)
            if service.is_time_to_charge():
                service.apply_storage_fee()


def get_listing_user_role(request: Request, listing: Listing, view: object):
    data = {}
    if IsTagOwner().has_object_permission(request, view, listing):
        data["role"] = "HOST_STORE"
    elif IsItemOwner().has_object_permission(request, view, listing.item):
        data["role"] = "ITEM_OWNER"
    elif IsStoreUser().has_permission(request, view):
        data["role"] = "NON_HOST_STORE"
    else:
        data["role"] = "GUEST"
    return data
