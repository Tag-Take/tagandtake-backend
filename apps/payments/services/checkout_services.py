import stripe
from typing import Dict

from apps.payments.models.transactions import ItemCheckoutSession
from apps.supplies.models import (
    StoreSupply,
    SupplyCheckoutItem,
    SuppliesCheckoutSession,
)
from apps.marketplace.models import ItemListing
from apps.payments.utils import from_stripe_amount
from apps.stores.models import StoreProfile as Store
from apps.common.constants import QUANTITY, PRICE, AMOUNT_TOTAL, ID, STATUS, PAYMENT_INTENT


class CheckoutSessionService:

    @staticmethod
    def create_item_checkout_session(
        session: stripe.checkout.Session,
        item_listing: ItemListing,
    ):
        ItemCheckoutSession.objects.create(
            item=item_listing.item_details,
            store=item_listing.store,
            session_id=session.id,
            
        )

    @staticmethod
    def create_supplies_checkout_session(
        session: stripe.checkout.Session, store: Store, line_items: list[Dict[str, str]]
    ):
        supplies_checkout_session = SuppliesCheckoutSession.objects.create(
            store=store, session_id=session.id
        )

        CheckoutSessionService.create_supply_checkout_items(
            supplies_checkout_session, store, line_items
        )

    @staticmethod
    def create_supply_checkout_items(
        session: SuppliesCheckoutSession, store, line_items: list[Dict[str, str]]
    ):
        try:
            for item_data in line_items:
                supply = StoreSupply.objects.get(stripe_price_id=item_data[PRICE])
                quantity = item_data[QUANTITY]

                SupplyCheckoutItem.objects.create(
                    checkout_session=session,
                    store=store,
                    supply=supply,
                    quantity=quantity,
                    item_price=supply.price,
                )

        except Exception as e:
            raise


    @staticmethod
    def update_item_checkout_session(event_data_obj: Dict[str, str]):
        try:
            session_id = event_data_obj[ID]
            session = ItemCheckoutSession.objects.get(session_id=session_id)
            session.status = event_data_obj[STATUS]
            session.payment_intent_id = event_data_obj[PAYMENT_INTENT]
            session.save()

        except Exception as e:
            raise

