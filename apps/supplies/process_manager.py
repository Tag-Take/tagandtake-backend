from typing import Dict, Any
import json

from django.db import transaction

from apps.supplies.services import SuppliesServices
from apps.payments.services.transaction_services import TransactionService
from apps.stores.models import StoreProfile as Store
from apps.supplies.processor_registry import PROCESSOR_REGISTRY
from apps.common.constants import PRICE, QUANTITY


class SuppliesPurchaseProcessManager:
    def __init__(self, transaction: Dict[str, Any], store: Store, supplies):
        self.transaction = transaction
        self.store = store
        self.supplies = supplies

    @transaction.atomic
    def process_supplies(self):
        try:
            self._create_supplies_order_items()

            for supply in self.supplies:
                processor_class = self._get_processor_class(supply[PRICE])
                if processor_class:
                    processor = processor_class(
                        store=self.store, multiplier=supply[QUANTITY]
                    )
                    processor.process()
        except Exception as e:
            raise f"Error processing supplies: {str(e)}"

    def _create_supplies_order_items(self):
        SuppliesServices.create_supplies_order_items(
            self.transaction, self.store, self.supplies
        )

    @staticmethod
    def _get_processor_class(supply):
        return PROCESSOR_REGISTRY.get(supply)
