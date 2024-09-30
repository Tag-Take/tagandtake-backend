from typing import Any, Dict
import json

from apps.marketplace.processors import ItemListingPurchaseProcessor
from apps.supplies.process_manager import SuppliesPurchaseProcessManager
from apps.stores.services.store_services import StoreService
from apps.payments.services.transaction_services import TransactionService
from apps.marketplace.services.listing_services import ItemListingService
from apps.notifications.emails.services.email_senders import (
    ListingEmailSender,
    SuppliesEmailSender,
)
from apps.payments.models.transactions import (
    SuppliesPaymentTransaction,
    ItemPaymentTransaction,
)
from apps.stores.models import StoreProfile as Store
from apps.members.models import MemberProfile as Member
from apps.marketplace.models import ItemListing
from apps.payments.processors import (
    ItemListingFailedPaymentProcessor,
    SuppliesFailedPaymentProcessor,
)
from apps.common.constants import (
    METADATA,
    PURCHASE,
    ITEM,
    SUPPLIES,
    ITEM_ID,
    STORE_ID,
    LINE_ITEMS,
)


class PaymentIntentSucceededHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj

    def handle(self):
        if self.payment_intent[METADATA][PURCHASE] == ITEM:
            listing = ItemListingService.get_item_listing_by_item_id(
                self.payment_intent[METADATA][ITEM_ID]
            )
            transaction = TransactionService().upsert_item_transaction(
                self.payment_intent
            )

            sold_listing = self._process_item_purchased(listing, transaction)

            self._send_item_notifications(sold_listing)

        elif self.payment_intent[METADATA][PURCHASE] == SUPPLIES:
            store = StoreService.get_store(self.payment_intent[METADATA][STORE_ID])
            supplies = json.loads(self.payment_intent[METADATA][LINE_ITEMS])
            transaction = TransactionService().upsert_supplies_transaction(
                self.payment_intent
            )

            self._process_supplies_purchased(transaction, store, supplies)

            self._send_supplies_notifications(store, supplies)

    @staticmethod
    def _process_item_purchased(
        listing: ItemListing, transaction: ItemPaymentTransaction
    ):
        processor = ItemListingPurchaseProcessor(
            listing,
            transaction,
        )
        return processor.process()

    @staticmethod
    def _process_supplies_purchased(
        transaction: SuppliesPaymentTransaction, store: Store, supplies
    ):
        processor = SuppliesPurchaseProcessManager(transaction, store, supplies)
        return processor.process_supplies()

    @staticmethod
    def _send_item_notifications(sold_listing):
        ListingEmailSender.send_listing_sold_email(sold_listing)
        ListingEmailSender.send_listing_purchased_email(sold_listing)

    @staticmethod
    def _send_supplies_notifications(store: Store, supplies):
        SuppliesEmailSender.send_supplies_purchased_email(store, supplies)
        # TODO:
        # Notify Us with the supplies that were purchased


class PaymentIntentFailedHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj

    def handle(self):
        if self.payment_intent[METADATA][PURCHASE] == ITEM:
            processor = ItemListingFailedPaymentProcessor(self.payment_intent)
            processor.process()
        elif self.payment_intent[METADATA][PURCHASE] == SUPPLIES:
            processor = SuppliesFailedPaymentProcessor(self.payment_intent)
            processor.process()
