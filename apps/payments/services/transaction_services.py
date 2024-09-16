from typing import Any, Dict

import stripe

from apps.payments.models.transactions import SuppliesPaymentTransaction
from apps.tagandtake.models import (
    SuppliesCheckoutSession,
)
from apps.marketplace.models import ItemListing
from apps.marketplace.models import Item
from apps.payments.models.transactions import ItemCheckoutSession
from apps.payments.models.transactions import (
    ItemPaymentTransaction,
    SuppliesPaymentTransaction,
    FailedItemPaymentTransaction,
    FailedSuppliesPaymentTransaction,
)
from apps.stores.models import StoreProfile as Store
from apps.payments.constants import event_id_field_map, event_status_field_map
from apps.payments.utils import from_stripe_amount
from apps.tagandtake.services import SuppliesHandler


class TransactionHandler:

    def update_or_create_transaction(self, event_data_obj: Dict[str, Any]):
        if event_data_obj["metadata"]["purchase"] == "item":
            TransactionModel = ItemPaymentTransaction
            get_transaction_data = self.get_item_transaction_data
        elif event_data_obj["metadata"]["purchase"] == "supplies":
            TransactionModel = SuppliesPaymentTransaction
            get_transaction_data = self.get_supplies_transaction_data
        else:
            raise ValueError("Purchase must be either 'item' or 'supplies'.")

        lookup_field = {
            event_id_field_map[event_data_obj["id"][:2]]: event_data_obj["id"],
        }
        transaction_data = get_transaction_data(event_data_obj)

        transaction, created = TransactionModel.objects.get_or_create(
            **lookup_field, defaults=transaction_data
        )

        return transaction

    @staticmethod
    def get_item_transaction_data(event_data_obj: Dict[str, Any]):
        item = Item.objects.get(id=event_data_obj["metadata"]["item_id"])
        store = Store.objects.get(id=event_data_obj["metadata"]["store_id"])

        transaction_data = {
            "amount": from_stripe_amount(
                event_data_obj.get("amount") or event_data_obj.get("amount_total")
            ),
            "item": item,
            "store": store,
            "seller": item.owner,
            "buyer_email": event_data_obj.get("customer_email")
            or event_data_obj.get("receipt_email"),
        }

        if event_status_field_map[event_data_obj["id"][:2]]:
            transaction_data["payment_status"] = event_data_obj['status']
        return transaction_data

    @staticmethod
    def get_supplies_transaction_data(event_data_obj: Dict[str, Any]):
        store = Store.objects.get(id=event_data_obj["metadata"]["store_id"])
        transaction_data = {
            "amount": event_data_obj["metadata"]["amount"],
            "store": store,
        }
        if event_status_field_map[event_data_obj["id"][:2]]:
            transaction_data["payment_status"] = event_status_field_map[
                event_data_obj["id"][:2]
            ]
        return transaction_data

    def handle_item_purchase_failed(
        payment_intent: Dict[str, Any], transaction: ItemPaymentTransaction
    ):
        return FailedItemPaymentTransaction.objects.create(
            payment_transaction=transaction,
            error_message=payment_intent["last_payment_error"]["message"],
            error_code=payment_intent["last_payment_error"]["code"],
        )

    def handle_supplies_purchase_failed(
        payment_intent, transaction: SuppliesPaymentTransaction
    ):
        return FailedSuppliesPaymentTransaction.objects.create(
            payment_transaction=transaction,
            error_message=payment_intent["last_payment_error"]["message"],
            error_code=payment_intent["last_payment_error"]["code"],
        )


class CheckoutSessionHandler:

    def save_supplies_checkout_session(
        session: stripe.checkout.Session, store: Store, line_items: list[Dict[str, str]]
    ):
        supplies_checkout_session = SuppliesCheckoutSession.objects.create(
            store=store, session_id=session.id
        )

        SuppliesHandler().save_supplies_checkout_session(
            supplies_checkout_session, store, line_items
        )

    def save_item_checkout_session(
        session: stripe.checkout.Session,
        item_listing: ItemListing,
    ):
        ItemCheckoutSession.objects.create(
            item=item_listing.item_details,
            store=item_listing.store,
            session_id=session.id,
        )
