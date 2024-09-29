from typing import Any, Dict
import stripe

from apps.payments.models.transactions import SuppliesPaymentTransaction
from apps.supplies.models import (
    StoreSupply,
    SupplyOrderItem
)
from apps.marketplace.models import Item
from apps.payments.models.transactions import (
    ItemPaymentTransaction,
    SuppliesPaymentTransaction,
    FailedItemPaymentTransaction,
    FailedSuppliesPaymentTransaction,
)
from apps.stores.models import StoreProfile as Store
from apps.payments.constants import EVENT_TYPE_ID_MAP
from apps.payments.utils import from_stripe_amount
from apps.common.constants import *


class TransactionService:

    def upsert_item_transaction(self, event_data_obj: Dict[str, Any]):
        event_id = TransactionService._get_event_id(event_data_obj)
        transaction_data = TransactionService._get_base_item_transaction_data(
            event_data_obj
        )
        transaction_data = TransactionService._add_payment_intent_status(
            transaction_data, event_data_obj
        )
        transaction, created = ItemPaymentTransaction.objects.get_or_create(
            **event_id, defaults=transaction_data
        )
        return transaction

    def upsert_supplies_transaction(self, event_data_obj: Dict[str, Any]):
        event_id = TransactionService._get_event_id(event_data_obj)
        transaction_data = TransactionService._get_supplies_transaction_data(
            event_data_obj
        )
        transaction_data = TransactionService._add_payment_intent_status(
            transaction_data, event_data_obj
        )
        transaction, created = SuppliesPaymentTransaction.objects.get_or_create(
            **event_id, defaults=transaction_data
        )

        return transaction

    @staticmethod
    def _get_event_id(event_data_obj: Dict[str, Any]):
        return {
            EVENT_TYPE_ID_MAP[event_data_obj[ID][:2]]: event_data_obj[ID],
        }

    @staticmethod
    def _get_base_item_transaction_data(event_data_obj: Dict[str, Any]):
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
    def _get_supplies_transaction_data(event_data_obj: Dict[str, Any]):
        return {
            AMOUNT: event_data_obj[METADATA][AMOUNT],
            STORE: Store.objects.get(id=event_data_obj[METADATA][STORE_ID]),
        }

    @staticmethod
    def _add_payment_intent_status(transaction_data, event_data_obj: Dict[str, Any]):
        if event_data_obj[ID].startswith("pi"):
            transaction_data[PAYMENT_STATUS] = event_data_obj[STATUS]
        return transaction_data

    @staticmethod
    def create_filed_item_transaction(
        payment_intent: Dict[str, Any], transaction: ItemPaymentTransaction
    ):
        return FailedItemPaymentTransaction.objects.create(
            payment_transaction=transaction,
            error_message=payment_intent[LAST_PAYMENT_ERROR][MESSAGE],
            error_code=payment_intent[LAST_PAYMENT_ERROR][CODE],
        )

    @staticmethod
    def create_failed_supplies_transaction(
        payment_intent, transaction: SuppliesPaymentTransaction
    ):
        return FailedSuppliesPaymentTransaction.objects.create(
            payment_transaction=transaction,
            error_message=payment_intent[LAST_PAYMENT_ERROR][MESSAGE],
            error_code=payment_intent[LAST_PAYMENT_ERROR][CODE],
        )
    

