import json
from typing import Dict, Any

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
from apps.common.constants import METADATA, ITEM_ID, STORE_ID, LINE_ITEMS


class BasePaymentProcessor:
    def __init__(self, payment_intent: Dict[str, Any]):
        self.payment_intent = payment_intent

    def process_payment_succeeded(self):
        raise NotImplementedError("Subclasses must implement process_purchase")

    def process_payment_failed(self):
        raise NotImplementedError("Subclasses must implement process_failed_payment")


class ItemPurchaseProcessor(BasePaymentProcessor):
    def process_payment_succeeded(self):
        listing = ItemListingService.get_item_listing_by_item_id(
            self.payment_intent[METADATA][ITEM_ID]
        )

        transaction = TransactionService().upsert_item_transaction(self.payment_intent)
        sold_listing = ItemListingPurchaseProcessor(listing, transaction).process()
        TransactionService().process_item_transaction(transaction)
        TransferService().run_post_success_transfers(self.payment_intent)

        ListingEmailSender.send_listing_sold_email(sold_listing)
        ListingEmailSender.send_listing_purchased_email(sold_listing)

    def process_payment_failed(self):
        TransactionService.create_failed_item_transaction(self.payment_intent)


class SuppliesPurchaseProcessor(BasePaymentProcessor):
    def process_payment_succeeded(self):
        store = StoreService.get_store(self.payment_intent[METADATA][STORE_ID])
        supplies = json.loads(self.payment_intent[METADATA][LINE_ITEMS])

        transaction = TransactionService().upsert_supplies_transaction(
            self.payment_intent
        )
        SuppliesPurchaseProcessManager(transaction, store, supplies).process_supplies()
        TransactionService().process_supplies_transaction(transaction)

        OperationsEmailSender.send_supplies_ordered_email(store, supplies)
        SuppliesEmailSender.send_supplies_purchased_email(store, supplies)

    def process_payment_failed(self):
        TransactionService.create_failed_supplies_transaction(self.payment_intent)
