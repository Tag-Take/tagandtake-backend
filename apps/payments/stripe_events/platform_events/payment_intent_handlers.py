from typing import Any, Dict
from apps.payments.processors import (
    BasePaymentProcessor,
    ItemPurchaseProcessor,
    SuppliesPurchaseProcessor,
)
from apps.common.constants import METADATA, PURCHASE, ITEM, SUPPLIES


class PaymentIntentSucceededHandler:
    processor_registry = {
        ITEM: ItemPurchaseProcessor,
        SUPPLIES: SuppliesPurchaseProcessor,
    }

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj
        self.purchase_type = self.payment_intent[METADATA][PURCHASE]
        self.processor: BasePaymentProcessor = self._get_processor()

    def _get_processor(self):
        processor_class = self.processor_registry.get(self.purchase_type)
        if not processor_class:
            raise ValueError(f"Unsupported purchase type: {self.purchase_type}")
        return processor_class(self.payment_intent)

    def handle(self):
        self.processor.process_payment_succeeded()


class PaymentIntentPaymentFailedHandler:
    processor_registry = {
        ITEM: ItemPurchaseProcessor,
        SUPPLIES: SuppliesPurchaseProcessor,
    }

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj
        self.purchase_type = self.payment_intent[METADATA][PURCHASE]
        self.processor: BasePaymentProcessor = self._get_processor()

    def _get_processor(self):
        processor_class = self.processor_registry.get(self.purchase_type)
        if not processor_class:
            raise ValueError(f"Unsupported purchase type: {self.purchase_type}")
        return processor_class(self.payment_intent)

    def handle(self):
        self.processor.process_payment_failed()
