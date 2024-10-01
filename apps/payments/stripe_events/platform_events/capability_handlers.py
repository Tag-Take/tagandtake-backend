from apps.payments.services.stripe_services import StripeService

class CapabilityUpdatedHandler:

    def __init__(self, event_data_obj: Dict[str, Any]):
        self.capability_update = event_data_obj
        self.account_type = self.capability_update["account_type"]

    def handle(self):
        pass
