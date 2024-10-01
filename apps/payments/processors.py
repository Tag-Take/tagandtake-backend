from typing import Dict, Any
from apps.common.abstract_classes import AbstractProcessor
from apps.payments.services.transaction_services import TransactionService


class ItemListingFailedPaymentProcessor(AbstractProcessor):

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj

    def process(self):
        self._create_failed_transaction()

    def _create_failed_transaction(self):
        TransactionService.create_failed_item_transaction(
            self.payment_intent
        )


class SuppliesFailedPaymentProcessor(AbstractProcessor):
    
    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj

    def process(self):
        self._create_failed_transaction()

    def _create_failed_transaction(self): 
        TransactionService.create_failed_supplies_transaction(
            self.payment_intent
        )