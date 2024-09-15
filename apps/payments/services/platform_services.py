import stripe

from apps.payments.models.transactions import SuppliesPaymentTransaction
from apps.tagandtake.models import (
    StoreSupply,
    SuppliesCheckoutSession,
    SupplyCheckoutItem,
)
from apps.stores.models import StoreProfile as Store


class SupplyTransactionHandler:
    def __init__(self, transaction: SuppliesPaymentTransaction):
        self.transaction = transaction


def save_supplies_checkout_session(
    session: stripe.checkout.Session, store: Store, line_items: list[dict]
):
    try:
        supplies_checkout_session = SuppliesCheckoutSession.objects.create(
            store=store, session_id=session.id
        )

        for item_data in line_items:
            supply = StoreSupply.objects.get(stripe_price_id=item_data["price"])
            quantity = item_data["quantity"]
            SupplyCheckoutItem.objects.create(
                checkout_session=supplies_checkout_session,
                supply=supply,
                quantity=quantity,
                item_price=supply.price,
            )

        return supplies_checkout_session

    except Exception as e:
        raise e
