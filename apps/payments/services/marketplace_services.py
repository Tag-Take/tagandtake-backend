from apps.payments.models.transactions import (
    ItemPaymentTransaction,
    ItemCheckoutSession,
)
import stripe
from apps.marketplace.models import ItemListing


class ItemTransactionHandler:
    def __init__(self, transaction: ItemPaymentTransaction):
        self.transaction = transaction


def save_item_checkout_session(
    item_listing: ItemListing, session: stripe.checkout.Session
):
    ItemCheckoutSession.objects.create(
        item=item_listing.item_details,
        store=item_listing.store,
        session_id=session.id,
    )
