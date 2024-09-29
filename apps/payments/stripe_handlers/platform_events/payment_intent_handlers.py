from typing import Any, Dict
from apps.marketplace.processors import ItemListingPurchaseProcessor
from apps.supplies.process_manager import SuppliesPurchaseProcessManager
from apps.payments.services.transaction_services import TransactionService
from apps.marketplace.services.listing_services import ItemListingService
from apps.notifications.emails.services.email_senders import ListingEmailSender
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
            listing = ItemListingService.get_item_listing_by_item_id(self.payment_intent[METADATA][ITEM_ID])
            transaction = TransactionService.upsert_item_transaction(self.payment_intent)

            processor = ItemListingPurchaseProcessor(
                listing, transaction,
            )
            sold_listing = processor.process()

            self._send_item_notifications(sold_listing)

        elif self.payment_intent[METADATA][PURCHASE] == SUPPLIES:
            transaction = TransactionService.upsert_supplies_transaction(self.payment_intent)

            processor = SuppliesPurchaseProcessManager(
                transaction, self.payment_intent[METADATA][STORE_ID], self.payment_intent[METADATA][LINE_ITEMS]
            )
            supplies = processor.process_supplies()

            self._send_supplies_notifications(supplies)

    @staticmethod
    def _send_item_notifications(sold_listing):
        ListingEmailSender.send_listing_sold_email(sold_listing)
        ListingEmailSender.send_listing_purchased_email(sold_listing)

    def _send_supplies_notifications(self, supplies):
        #TODO - Implement this
        # Notify Store
        # Notify Us with the supplies that were purchased
        pass

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
