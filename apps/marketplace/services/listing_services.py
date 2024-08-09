from datetime import timedelta
from django.db import transaction
from django.utils.timezone import now
from decimal import Decimal

from rest_framework import serializers

from apps.stores.models import Tag
from apps.marketplace.models import (
    Listing,
    RecalledListing,
    DelistedListing,
    SoldListing,
    RecallReason,
)
from apps.marketplace.services.pricing_services import (
    RECALLED_LISTING_RECURRING_FEE,
    GRACE_PERIOD_DAYS,
    RECURRING_FEE_INTERVAL_DAYS,
)
from apps.emails.services.email_senders import ListingEmailSender


class ListingHandler:
    def __init__(self, listing=None):
        self.listing = listing

    @staticmethod
    def create_listing(item, tag, store_commission, min_listing_days):
        with transaction.atomic():
            listing = Listing.objects.create(
                item=item,
                tag=tag,
                store_commission=store_commission,
                min_listing_days=min_listing_days,
            )
            item.status = "Listed"
            item.save()
            ListingEmailSender(listing).send_listed_created_email()
        return listing

    @staticmethod
    def create_item_and_listing(serializer, request):
        with transaction.atomic():
            item = serializer.save()
            tag_id = request.data.get("tag_id")

            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise serializers.ValidationError("Tag does not exist.")

            store_commission = tag.store.commission
            min_listing_days = tag.store.min_listing_days

            listing = ListingHandler.create_listing(
                item=item,
                tag=tag,
                store_commission=store_commission,
                min_listing_days=min_listing_days,
            )
            item.status = "listed"
            item.save()
            ListingEmailSender(listing).send_listed_created_email()
            return listing

    def recall_listing(self, reason_id):
        try:
            reason = self.get_recall_reasons(reason_id)
            with transaction.atomic():
                RecalledListing.objects.create(
                    tag=self.listing.tag,
                    item=self.listing.item,
                    store_commission=self.listing.store_commission,
                    min_listing_days=self.listing.min_listing_days,
                    reason=reason,
                    next_fee_charge_at=now()
                    + timedelta(days=self.get_grace_period_days()),
                )
                self.listing.item.status = "recalled"
                self.listing.item.save()
                self.listing.delete()
                ListingEmailSender(self.listing).send_listing_recalled_email(reason)
        except RecallReason.DoesNotExist:
            raise serializers.ValidationError("Invalid reason provided")

    def apply_recurring_storage_fee(self):
        with transaction.atomic():
            self.listing.fee_charged_count += 1
            self.listing.last_fee_charge_at = now()
            self.listing.last_fee_charge_amount = (
                self.listing.last_fee_charge_amount or Decimal("0.00")
            ) + RECALLED_LISTING_RECURRING_FEE
            self.listing.next_fee_charge_at = now() + timedelta(
                days=self.get_recurring_fee_interval_days()
            )
            self.listing.save()
            ListingEmailSender(self.listing).send_storage_fee_charged_email()

    def delist_listing(self, reason_id):
        try:
            reason = self.get_recall_reasons(reason_id)
            with transaction.atomic():
                DelistedListing.objects.create(
                    tag=self.listing.tag,
                    item=self.listing.item,
                    store_commission=self.listing.store_commission,
                    min_listing_days=self.listing.min_listing_days,
                    reason=reason,
                )
                self.listing.item.status = "available"
                self.listing.item.save()
                self.listing.delete()
                ListingEmailSender(self.listing).send_listing_delisted_email()
        except RecallReason.DoesNotExist:
            raise serializers.ValidationError("Invalid reason provided")

    def delist_recalled_listing(self):
        with transaction.atomic():
            DelistedListing.objects.create(
                tag=self.listing.tag,
                item=self.listing.item,
                store_commission=self.listing.store_commission,
                min_listing_days=self.listing.min_listing_days,
                reason=self.listing.reason,
            )
            self.listing.item.status = "available"
            self.listing.item.save()
            self.listing.delete()
            ListingEmailSender(self.listing).send_listing_collected_email()

    def purchase_listing(self, buyer):
        if self.listing:
            with transaction.atomic():
                SoldListing.objects.create(
                    tag=self.listing.tag,
                    item=self.listing.item,
                    store_commission=self.listing.store_commission,
                    min_listing_days=self.listing.min_listing_days,
                    buyer=buyer,
                )
                self.listing.item.status = "sold"
                self.listing.item.save()
                self.listing.delete()
                ListingEmailSender(self.listing).send_listing_sold_email()

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
        ListingEmailSender(self.recalled_listing).send_collection_reminder_email()

    @staticmethod
    def run_storage_fee_reminder_checks():
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
        ListingHandler(self.recalled_listing).apply_recurring_storage_fee()

    @staticmethod
    def run_storage_fee_checks():
        recalled_listings = RecalledListing.objects.all()
        for recalled_listing in recalled_listings:
            service = RecalledListingStorageFeeService(recalled_listing)
            if service.is_time_to_charge():
                service.apply_storage_fee()
