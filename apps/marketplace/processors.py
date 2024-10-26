from django.db import transaction

from apps.common.abstract_classes import AbstractProcessor
from apps.marketplace.services.listing_services import ItemListingService
from apps.notifications.emails.services.email_senders import ListingEmailSender
from apps.items.models import Item
from apps.stores.models import Tag
from apps.items.services import ItemService
from apps.marketplace.models import ItemListing, RecalledItemListing, RecallReason
from apps.payments.models.transactions import ItemPaymentTransaction


class ItemListingCreateProcessor(AbstractProcessor):
    def __init__(self, item: Item, tag: Tag):
        self.item = item
        self.tag = tag

    @transaction.atomic
    def process(self):
        listing = ItemListingService.create_listing(self.item, self.tag)
        ItemService.list_item(self.item)
        ListingEmailSender.send_listing_created_email(listing)
        return listing


class ItemListingRecallProcessor(AbstractProcessor):
    def __init__(self, listing: ItemListing, reason: RecallReason):
        self.listing = listing
        self.reason = reason

    @transaction.atomic
    def process(self):
        recalled_listing = ItemListingService.create_recalled_listing(
            self.listing, self.reason
        )
        ItemService.recall_item(recalled_listing.item)
        ItemListingService.delete_listing(self.listing)
        ListingEmailSender.send_listing_recalled_email(recalled_listing, self.reason)
        return recalled_listing


class ItemListingDelistProcessor(AbstractProcessor):
    def __init__(self, listing: ItemListing, reason: RecallReason):
        self.listing = listing
        self.reason = reason

    @transaction.atomic
    def process(self):
        delisted_listing = ItemListingService.create_delisted_listing(
            self.listing, self.reason
        )
        ItemService.delist_item(delisted_listing.item)
        ItemListingService.delete_listing(self.listing)
        ListingEmailSender.send_listing_delisted_email(delisted_listing)
        return delisted_listing


class ItemListingCollectProcessor(AbstractProcessor):
    def __init__(self, listing: RecalledItemListing):
        self.recalled_listing = listing

    @transaction.atomic
    def process(self):
        delisted_listing = ItemListingService.create_delisted_listing(
            self.recalled_listing, self.recalled_listing.reason
        )
        ItemService.collect_item(delisted_listing.item)
        ItemListingService.delete_recalled_listing(self.recalled_listing)
        ListingEmailSender.send_recalled_listing_collected_email(delisted_listing)
        return delisted_listing


class ItemListingReplaceTagProcessor(AbstractProcessor):
    def __init__(self, listing: ItemListing, tag: Tag):
        self.listing = listing
        self.tag = tag

    def process(self):
        return ItemListingService.replace_listing_tag(self.listing, self.tag)


class CollectionPinUpdateProcessor(AbstractProcessor):
    def __init__(self, listing: RecalledItemListing):
        self.recalled_listing = listing

    def process(self):
        ItemListingService.update_recalled_listing_collection_pin(self.recalled_listing)
        ListingEmailSender.send_new_collection_pin_email(self.recalled_listing)
        return self.recalled_listing


class ItemListingAbandonedProcessor(AbstractProcessor):
    def __init__(self, recalled_listing: RecalledItemListing):
        self.recalled_listing = recalled_listing

    @transaction.atomic
    def process(self):
        delisted_listing = ItemListingService.create_delisted_listing(
            self.recalled_listing, self.recalled_listing.reason
        )
        ItemService.abandon_item(delisted_listing.item)
        ItemListingService.delete_recalled_listing(self.recalled_listing)
        ListingEmailSender.send_item_abandonded_email(self.recalled_listing)
        return self.recalled_listing


class ItemListingPurchaseProcessor(AbstractProcessor):
    def __init__(
        self, listing: ItemListing, payment_trasaction: ItemPaymentTransaction
    ):
        self.listing = listing
        self.transaction = payment_trasaction

    @transaction.atomic
    def process(self):
        sold_listing = ItemListingService.create_sold_listing(
            self.listing, self.transaction
        )
        ItemListingService.delete_listing(self.listing)
        ItemService.purchase_item(sold_listing.item)
        return sold_listing
