from typing import Any, Dict
from apps.marketplace.processors import ItemListingPurchaseProcessor
from apps.stores.handlers import SuppliesPurchaseHandler
from apps.supplies.processors import SuppliesPurchaseProcessManager
from apps.payments.processors import (
    ItemListingFailedPaymentProcessor,
    SuppliesFailedPaymentProcessor,
)
from apps.common.constants import (
    METADATA,
    PURCHASE,
    ITEM,
    SUPPLIES,
)


class PaymentIntentSucceededHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.payment_intent = event_data_obj

    def handle(self):
        if self.payment_intent[METADATA][PURCHASE] == ITEM:
            processor = ItemListingPurchaseProcessor(self.payment_intent)
            processor.process()
        elif self.payment_intent[METADATA][PURCHASE] == SUPPLIES:
            handler = SuppliesPurchaseProcessManager(self.payment_intent)
            handler.process_supplies()


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
