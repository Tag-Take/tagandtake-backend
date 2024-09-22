from django.db import transaction

from apps.common.abstract_classes import AbstractHandler
from apps.marketplace.services.listing_services import ItemListingService
from apps.notifications.emails.services.email_senders import ListingEmailSender
from apps.items.models import Item
from apps.stores.models import Tag
from apps.items.services import ItemService
from apps.marketplace.models import ItemListing, RecalledItemListing, RecallReason


class ItemListingCreateHandler(AbstractHandler):
    def __init__(self, item: Item, tag: Tag):
        self.item = item
        self.tag = tag

    @transaction.atomic
    def handle(self):
        listing = self._create_item_listing()
        self._list_item()
        self._send_notifications(listing)
        return listing

    def _create_item_listing(self):
        return ItemListingService.create_listing(self.item, self.tag)

    def _list_item(self):
        ItemService.list_item(self.item)

    @staticmethod
    def _send_notifications(listing):
        ListingEmailSender.send_listing_created_email(listing)


class ItemListingRecallHandler(AbstractHandler):
    def __init__(self, listing: ItemListing, reason: RecallReason):
        self.listing = listing
        self.reason = reason

    @transaction.atomic
    def handle(self):
        recalled_listing = self._create_recalled_listing()
        self._recall_item(recalled_listing.item)
        self._delete_listing()
        self._send_notifications(recalled_listing)
        return recalled_listing

    def _create_recalled_listing(self):
        return ItemListingService.create_recalled_listing(self.listing, self.reason)

    @staticmethod
    def _recall_item(item):
        ItemService.recall_item(item)

    def _delete_listing(self):
        ItemListingService.delete_listing(self.listing)

    def _send_notifications(self, recalled_listing):
        ListingEmailSender.send_listing_recalled_email(recalled_listing, self.reason)


class ItemListingDelistHandler(AbstractHandler):
    def __init__(self, listing: ItemListing, reason: RecallReason):
        self.listing = listing
        self.reason = reason

    @transaction.atomic
    def handle(self):
        delisted_listing = self._create_delisted_listing()
        self._delist_item(delisted_listing.item)
        self._delete_listing()
        self._send_notifications(delisted_listing)
        return delisted_listing

    def _create_delisted_listing(self):
        return ItemListingService.create_delisted_listing(self.listing, self.reason)

    @staticmethod
    def _delist_item(item):
        ItemService.delist_item(item)

    def _delete_listing(self):
        ItemListingService.delete_listing(self.listing)

    @staticmethod
    def _send_notifications(delisted_listing):
        ListingEmailSender.send_listing_delisted_email(delisted_listing)


class ItemListingCollectHandler(AbstractHandler):
    def __init__(self, listing: RecalledItemListing):
        self.recalled_listing = listing

    @transaction.atomic
    def handle(self):
        delisted_listing = self._create_delisted_listing()
        self._collect_item(delisted_listing.item)
        self._delete_recalled_listing()
        self._send_notifications(delisted_listing)
        return delisted_listing

    def _create_delisted_listing(self):
        return ItemListingService.create_delisted_listing(
            self.recalled_listing, self.recalled_listing.reason
        )

    @staticmethod
    def _collect_item(item):
        ItemService.collect_item(item)

    def _delete_recalled_listing(self):
        ItemListingService.delete_recalled_listing(self.recalled_listing)

    @staticmethod
    def _send_notifications(delisted_listing):
        ListingEmailSender.send_recalled_listing_collected_email(delisted_listing)


class ReplaceListingTagHandler(AbstractHandler):
    def __init__(self, listing: ItemListing, tag: Tag):
        self.listing = listing
        self.tag = tag

    def handle(self):
        self._replace_tag(self.listing, self.tag)
        return self.listing

    @staticmethod
    def _replace_tag(listing, tag):
        return ItemListingService.replace_listing_tag(listing, tag)


class GenerateNewCollectionPinHandler(AbstractHandler):
    def __init__(self, listing: RecalledItemListing):
        self.recalled_listing = listing

    def handle(self):
        self._update_collection_pin()
        self._send_notifications()
        return self.recalled_listing

    def _update_collection_pin(self):
        return ItemListingService.update_recalled_listing_collection_pin(
            self.recalled_listing
        )

    def _send_notifications(self):
        ListingEmailSender.send_new_collection_pin_email(self.recalled_listing)


class ItemListingAbandonedHandler(AbstractHandler):
    def __init__(self, recalled_listing: RecalledItemListing):
        self.recalled_listing = recalled_listing

    @transaction.atomic
    def handle(self):
        delisted_listing = self._create_delisted_listing()
        self._abandon_item(delisted_listing.item)
        self._delete_recalled_listing()
        self._send_notifications()
        return self.recalled_listing

    def _create_delisted_listing(self):
        return ItemListingService.create_delisted_listing(
            self.recalled_listing, self.recalled_listing.reason
        )

    @staticmethod
    def _abandon_item(item):
        ItemService.abandon_item(item)

    def _delete_recalled_listing(self):
        ItemListingService.delete_recalled_listing(self.recalled_listing)

    def _send_notifications(self):
        ListingEmailSender.send_item_abandonded_email(self.recalled_listing)
