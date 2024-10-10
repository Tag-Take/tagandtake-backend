from typing import Any, Dict
import json

from apps.marketplace.processors import ItemListingPurchaseProcessor
from apps.supplies.process_manager import SuppliesPurchaseProcessManager
from apps.stores.services.store_services import StoreService
from apps.payments.services.transaction_services import TransactionService
from apps.payments.services.transfer_services import TransferService
from apps.marketplace.services.listing_services import ItemListingService
from apps.notifications.emails.services.email_senders import (
    ListingEmailSender,
    SuppliesEmailSender,
    OperationsEmailSender,
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
        self.purchase_type = self.payment_intent[METADATA][PURCHASE]

    def handle(self):
        if self.purchase_type == ITEM:
            listing = self._get_listing()
            transaction = self._create_item_transaction()
            sold_listing = self._process_item_purchased(listing, transaction)
            self._update_item_transaction_as_processed(transaction)
            self._run_post_success_transfers()
            self._send_item_notifications(sold_listing)

        elif self.purchase_type == SUPPLIES:
            store, supplies = self._get_store_and_supplies()
            transaction = self._create_supplies_transaction()
            self._process_supplies_purchased(transaction, store, supplies)
            self._update_supplies_transaction_as_processed(transaction)
            self._send_supplies_notifications(store, supplies)

    def _get_listing(self):
        return ItemListingService.get_item_listing_by_item_id(
            self.payment_intent[METADATA][ITEM_ID]
        )

    def _get_store_and_supplies(self):
        store = StoreService.get_store(self.payment_intent[METADATA][STORE_ID])
        supplies = json.loads(self.payment_intent[METADATA][LINE_ITEMS])
        return store, supplies

    def _create_item_transaction(self):
        return TransactionService().upsert_item_transaction(self.payment_intent)

    def _create_supplies_transaction(self):
        return TransactionService().upsert_supplies_transaction(self.payment_intent)

    @staticmethod
    def _process_item_purchased(
        listing: ItemListing, transaction: ItemPaymentTransaction
    ):
        return ItemListingPurchaseProcessor(
            listing,
            transaction,
        ).process()

    @staticmethod
    def _process_supplies_purchased(
        transaction: SuppliesPaymentTransaction, store: Store, supplies: Dict[str, str]
    ):
        return SuppliesPurchaseProcessManager(
            transaction, store, supplies
        ).process_supplies()

    @staticmethod
    def _update_item_transaction_as_processed(transaction):
        return TransactionService().process_item_transaction(transaction)

    @staticmethod
    def _update_supplies_transaction_as_processed(transaction):
        return TransactionService().process_supplies_transaction(transaction)

    def _run_post_success_transfers(self):
        TransferService().run_post_success_transfers(self.payment_intent)

    @staticmethod
    def _send_item_notifications(sold_listing):
        ListingEmailSender.send_listing_sold_email(sold_listing)
        ListingEmailSender.send_listing_purchased_email(sold_listing)

    @staticmethod
    def _send_supplies_notifications(store: Store, supplies: Dict[str, str]):
        OperationsEmailSender.send_supplies_ordered_email(store, supplies)
        SuppliesEmailSender.send_supplies_purchased_email(store, supplies)


class PaymentIntentPaymentFailedHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj

    def handle(self):
        if self.payment_intent[METADATA][PURCHASE] == ITEM:
            processor = ItemListingFailedPaymentProcessor(self.payment_intent)
            processor.process()
        elif self.payment_intent[METADATA][PURCHASE] == SUPPLIES:
            processor = SuppliesFailedPaymentProcessor(self.payment_intent)
            processor.process()

    def _get_listing(self):
        return ItemListingService.get_item_listing_by_item_id(
            self.payment_intent[METADATA][ITEM_ID]
        )

    def _get_store_and_supplies(self):
        store = StoreService.get_store(self.payment_intent[METADATA][STORE_ID])
        supplies = json.loads(self.payment_intent[METADATA][LINE_ITEMS])
        return store, supplies
