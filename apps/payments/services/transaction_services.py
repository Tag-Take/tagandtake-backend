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
from apps.payments.constants import EVENT_TYPE_ID_MAP, EVENT_STATUS_FIELD_MAP
from apps.payments.utils import from_stripe_amount
from apps.tagandtake.services import SuppliesHandler
from apps.common.constants import *


class TransactionService:

    def update_or_create_item_transaction(self, event_data_obj: Dict[str, Any]):
        event_id = {
            EVENT_TYPE_ID_MAP[event_data_obj[ID][:2]]: event_data_obj[ID],
        }
        transaction_data = self.get_base_item_transaction_data(event_data_obj)
        transaction_data = self.add_payment_intent_status(transaction_data, event_data_obj)
        transaction, created = ItemPaymentTransaction.objects.get_or_create(
            **event_id, defaults=transaction_data
        )
        return transaction

    def update_or_create_supplies_transaction(self, event_data_obj: Dict[str, Any]):
        lookup_field = {
            EVENT_TYPE_ID_MAP[event_data_obj[ID][:2]]: event_data_obj[ID],
        }
        transaction_data = self.get_supplies_transaction_data(event_data_obj)
        transaction, created = SuppliesPaymentTransaction.objects.get_or_create(
            **lookup_field, defaults=transaction_data
        )

        return transaction

    @staticmethod
    def get_base_item_transaction_data(event_data_obj: Dict[str, Any]):
        item = Item.objects.get(id=event_data_obj[METADATA][ITEM_ID])
        return {
            AMOUNT: from_stripe_amount(
                event_data_obj.get(AMOUNT) or event_data_obj.get(AMOUNT_TOTAL)
            ),
            ITEM: item,
            STORE: Store.objects.get(id=event_data_obj[METADATA][STORE_ID]),
            SELLER: item.owner,
            BUYER_EMAIL: event_data_obj.get(CUSTOMER_EMAIL)
            or event_data_obj.get(RECEIPT_EMAIL),
        }

    @staticmethod
    def add_payment_intent_status(transaction_data, event_data_obj: Dict[str, Any]):
        if event_data_obj[ID].startswith("pi"):
            transaction_data[PAYMENT_STATUS] = event_data_obj[STATUS]
        return transaction_data

    @staticmethod
    def get_supplies_transaction_data(event_data_obj: Dict[str, Any]):
        store = Store.objects.get(id=event_data_obj[METADATA][STORE_ID])
        transaction_data = {
            AMOUNT: event_data_obj[METADATA][AMOUNT],
            STORE: store,
        }
        if EVENT_STATUS_FIELD_MAP[event_data_obj[ID][:2]]:
            transaction_data[PAYMENT_STATUS] = EVENT_STATUS_FIELD_MAP[
                event_data_obj[ID][:2]
            ]
        return transaction_data

    def handle_item_purchase_failed(
        payment_intent: Dict[str, Any], transaction: ItemPaymentTransaction
    ):
        return FailedItemPaymentTransaction.objects.create(
            payment_transaction=transaction,
            error_message=payment_intent[LAST_PAYMENT_ERROR][MESSAGE],
            error_code=payment_intent[LAST_PAYMENT_ERROR][CODE],
        )

    def handle_supplies_purchase_failed(
        payment_intent, transaction: SuppliesPaymentTransaction
    ):
        return FailedSuppliesPaymentTransaction.objects.create(
            payment_transaction=transaction,
            error_message=payment_intent[LAST_PAYMENT_ERROR][MESSAGE],
            error_code=payment_intent[LAST_PAYMENT_ERROR][CODE],
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
