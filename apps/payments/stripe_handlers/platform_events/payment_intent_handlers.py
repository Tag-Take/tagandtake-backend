from typing import Any, Dict
from apps.payments.services.transaction_services import TransactionHandler
from apps.payments.services.transfer_services import TransferHandler
from apps.marketplace.services.listing_services import ItemListingHandler
from apps.marketplace.utils import get_item_listing_by_item_id
from apps.emails.services.email_senders import ListingEmailSender
from apps.stores.models import StoreProfile as Store
from apps.tagandtake.services import SuppliesHandler


class PaymentIntentSucceededHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj
        self.transaction = TransactionHandler().update_or_create_transaction(
            self.payment_intent
        )

    def handle(self):
        print('purchase', self.payment_intent["metadata"]["purchase"])
        if self.payment_intent["metadata"]["purchase"] == "item":
            print('handling item listing purchase')
            self.handle_item_listing_purchase()
        elif self.payment_intent["metadata"]["purchase"] == "supplies":
            self.handle_supplies_purchase()

    def handle_item_listing_purchase(self):
        item_listing = get_item_listing_by_item_id(
            self.payment_intent["metadata"]["item_id"]
        )
        try:
            ItemListingHandler.purchase_listing(item_listing, self.transaction)
            TransferHandler().run_post_success_transfers(self.payment_intent)
            ListingEmailSender.send_listing_sold_email(item_listing)
            # Jey TODO: Send email to store owner with the list of supplies bought
            # ListingEmailSender.send_listing_bought_email(item_listing)

        except Exception as e:
            print(f"Error occurred when handling payment intent: {str(e)}")

    def handle_supplies_purchase(self):
        line_items = self.payment_intent["metadata"]["line_items"]
        store = Store.objects.get(id=self.payment_intent["metadata"]["store_id"])

        try:
            SuppliesHandler().purchase_supplies(self.transaction, line_items, store)
            # Jey TODO: Send email to store owner with the list of supplies bought
            # ListingEmailSender.send_supplies_bought_email(store, line_items)

            # Dan TODO: Business logic for handling supplies purchase

        except Exception as e:
            print(f"Error occurred when handling payment intent: {str(e)}")


class PaymentIntentFailedHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj
        self.transaction = TransactionHandler().update_or_create_transaction(
            event_data_obj
        )

    def handle(self):
        if self.payment_intent["metadata"]["purchase"] == "item":
            TransactionHandler().handle_item_purchase_failed(
                self.payment_intent, self.transaction
            )
        elif self.payment_intent["metadata"]["purchase"] == "supplies":
            TransactionHandler().handle_supplies_purchase_failed(
                self.payment_intent, self.transaction
            )