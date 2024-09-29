from typing import Dict, Any

from django.db import transaction

from apps.supplies.services import SuppliesServices
from apps.payments.services.transaction_services import TransactionService
from apps.supplies.processor_registry import PROCESSOR_REGISTRY
from apps.common.constants import PRICE, QUANTITY


class SuppliesPurchaseProcessManager:
    def __init__(self, transaction: Dict[str, Any], store_id, line_items):
        self.transaction = transaction
        self.store_id = store_id
        self.supplies_list = line_items

    @transaction.atomic
    def process_supplies(self):
        self._create_supplies_order_items()

        for supply in self.supplies_list:
            processor_class = self._get_processor_class(supply[PRICE])
            if processor_class:
                processor = processor_class()
                processor.process(self.store_id, supply[QUANTITY])

    def _create_supplies_order_items(self):
        SuppliesServices.create_supplies_order_items(
            self.transaction, self.store_id, self.supplies_list
        )

    def _get_processor_class(supply):
        return PROCESSOR_REGISTRY.get(supply)
