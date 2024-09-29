from typing import Any, Dict
from apps.payments.services.transaction_services import TransactionService
from apps.common.constants import METADATA, PURCHASE, ITEM, SUPPLIES, ID


class CheckoutSessionCompletedHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.checkout_session = event_data_obj
        self.purchase_type = self.checkout_session[METADATA][PURCHASE]

    def handle(self):

        if self.purchase_type == ITEM:
            print(f"Item purchase. Upserting item transaction for checkout session: {self.checkout_session[ID]}")
            TransactionService().upsert_item_transaction(self.checkout_session)
        elif self.purchase_type == SUPPLIES:
            TransactionService().upsert_supplies_transaction(self.checkout_session)
        else:
            raise ValueError(f"Invalid purchase type{self.purchase_type}")
