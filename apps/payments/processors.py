import json
from typing import Dict, Any
from abc import ABC, abstractmethod

from rest_framework import serializers

from apps.marketplace.processors import ItemListingPurchaseProcessor
from apps.supplies.process_manager import SuppliesPurchaseProcessManager
from apps.payments.services.transaction_services import TransactionService
from apps.payments.services.transfer_services import TransferService
from apps.notifications.emails.services.email_senders import (
    ListingEmailSender,
    SuppliesEmailSender,
    OperationsEmailSender,
)
from apps.stores.models import StoreProfile as Store
from apps.marketplace.models import ItemListing
from apps.common.constants import METADATA, ITEM_ID, STORE_ID, LINE_ITEMS


class BasePaymentProcessor(ABC):
    def __init__(self, payment_intent: Dict[str, Any]):
        self.payment_intent = payment_intent

    @abstractmethod
    def process_payment_succeeded(self):
        pass

    @abstractmethod
    def process_payment_failed(self):
        pass

class ItemPurchaseProcessor(BasePaymentProcessor):
    def get_listing(self, item_id: int):
        try:
            return ItemListing.objects.get(id=item_id)
        except ItemListing.DoesNotExist:
            raise serializers.ValidationError("Listing does not exist.")

    def process_payment_succeeded(self):
        listing = self.get_listing(self.payment_intent[METADATA][ITEM_ID])

        transaction = TransactionService().upsert_item_transaction(self.payment_intent)
        sold_listing = ItemListingPurchaseProcessor(listing, transaction).process()
        TransactionService().process_item_transaction(transaction)
        TransferService().run_post_success_transfers(self.payment_intent)

        ListingEmailSender.send_listing_sold_email(sold_listing)
        ListingEmailSender.send_listing_purchased_email(sold_listing)

    def process_payment_failed(self):
        TransactionService.create_failed_item_transaction(self.payment_intent)


class SuppliesPurchaseProcessor(BasePaymentProcessor):
    def get_store(self, store_id: int):
        try:
            return Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise serializers.ValidationError("Store does not exist.")

    def process_payment_succeeded(self):
        store = self.get_store(self.payment_intent[METADATA][STORE_ID])
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
