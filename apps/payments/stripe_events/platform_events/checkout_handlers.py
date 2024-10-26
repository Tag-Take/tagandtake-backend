from typing import Any, Dict
from apps.payments.services.checkout_services import CheckoutSessionService
from apps.common.constants import METADATA, PURCHASE, ITEM, SUPPLIES


class CheckoutSessionCompletedHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.checkout_session = event_data_obj
        self.purchase_type = self.checkout_session[METADATA][PURCHASE]

    def handle(self):

        if self.purchase_type == ITEM:
            CheckoutSessionService.update_item_checkout_session(self.checkout_session)
        elif self.purchase_type == SUPPLIES:
            CheckoutSessionService.update_supplies_checkout_session(
                self.checkout_session
            )
        else:
            raise ValueError(f"Invalid purchase type{self.purchase_type}")
