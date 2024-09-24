from typing import Any, Dict
from apps.payments.services.transaction_services import TransactionService


class CheckoutSessionCompletedHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.checkout_session = event_data_obj

    def handle(self):
        TransactionService().update_or_create_transaction(self.checkout_session)
