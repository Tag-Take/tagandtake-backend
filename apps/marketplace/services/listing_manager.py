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
from apps.marketplace.services.pricing import (
    RECALLED_LISTING_RECURRING_FEE,
    GRACE_PERIOD_DAYS,
    RECURRING_FEE_INTERVAL_DAYS
)
from apps.emails.services.email_senders import ItemEmailSender


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
            ItemEmailSender(listing).send_item_listed_email()
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
            ItemEmailSender(listing).send_item_listed_email()
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
                    next_fee_charge_at=now() #TODO: REMOVE!!!!
                #     + timedelta(
                #         days=self.get_grace_period_days()
                #         )  
                )
                self.listing.item.status = "recalled"
                self.listing.item.save()
                self.listing.delete()
                ItemEmailSender(self.listing).send_item_recalled_email(reason)
        except RecallReason.DoesNotExist:
            raise serializers.ValidationError("Invalid reason provided")

    def apply_recurring_storage_fee(self):
        try:
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
                ItemEmailSender(self.listing).send_storage_fee_charged_email()
        except RecalledListing.DoesNotExist:
            raise serializers.ValidationError("Recalled listing not found.")

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
                ItemEmailSender(self.listing).send_item_delisted_email()
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
            ItemEmailSender(self.listing).send_item_collected_email()

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
                ItemEmailSender(self.listing).send_item_sold_email()


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

