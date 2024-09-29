from typing import Any, Dict

from django.db import transaction   

from apps.payments.models.transactions import SuppliesPaymentTransaction
from apps.payments.models.transactions import (
    ItemPaymentTransaction,
    SuppliesPaymentTransaction,
    FailedItemPaymentTransaction,
    FailedSuppliesPaymentTransaction,
)
from apps.items.services import ItemService
from apps.stores.services.store_services import StoreService
from apps.payments.services.stripe_services import StripeService
from apps.stores.models import StoreProfile as Store
from apps.payments.utils import from_stripe_amount
from apps.common.constants import *


class TransactionService:

    @transaction.atomic
    def upsert_item_transaction(self, event_data_obj: Dict[str, Any]):
        event_id = {PAYMENT_INTENT_ID: event_data_obj[ID]}
        transaction_data = TransactionService._get_base_item_transaction_data(
            event_data_obj
        )
        transaction, created = ItemPaymentTransaction.objects.get_or_create(
            **event_id, defaults=transaction_data
        )

        if not created:
            for key, value in transaction_data.items():
                setattr(transaction, key, value)

            transaction.save()

        return transaction
    
    @transaction.atomic
    def upsert_supplies_transaction(self, event_data_obj: Dict[str, Any]):
        event_id = {PAYMENT_INTENT_ID: event_data_obj[ID]}
        transaction_data = TransactionService._get_supplies_transaction_data(
            event_data_obj
        )
        transaction, created = SuppliesPaymentTransaction.objects.get_or_create(
            **event_id, defaults=transaction_data
        )

        if not created:
            for key, value in transaction_data.items():
                setattr(transaction, key, value)

            transaction.save()

        return transaction

    @staticmethod
    def _get_base_item_transaction_data(event_data_obj: Dict[str, Any]):
        amount = from_stripe_amount(event_data_obj[AMOUNT])
        item = ItemService.get_item(id=event_data_obj[METADATA][ITEM_ID])
        store = StoreService.get_store(id=event_data_obj[METADATA][STORE_ID])
        buyer_email = StripeService.get_buyer_email_from_payment_intent(event_data_obj[ID])
        return {
            AMOUNT: amount,
            ITEM: item,
            STORE: store,
            MEMBER: item.owner,
            STORE_COMMISSION: event_data_obj[METADATA][STORE_AMOUNT],
            MEMBER_EARNINGS: event_data_obj[METADATA][MEMBER_EARNINGS],
            TRANSACTION_FEE: event_data_obj[METADATA][TRANSACTION_FEE],
            STATUS: event_data_obj[STATUS],
            BUYER_EMAIL: buyer_email,
            LATEST_CHARGE: event_data_obj[LATEST_CHARGE],
        }

    @staticmethod
    def _get_supplies_transaction_data(event_data_obj: Dict[str, Any]):
        return {
            AMOUNT: event_data_obj[METADATA][AMOUNT],
            STORE: Store.objects.get(id=event_data_obj[METADATA][STORE_ID]),
            STATUS: event_data_obj[STATUS],
        }

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
    

