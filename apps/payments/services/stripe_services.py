from typing import Dict
from django.conf import settings
import stripe
from apps.payments.models.accounts import StorePaymentAccount
from apps.marketplace.models import ItemListing
from apps.payments.utils import to_stripe_amount

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_account(business_type: str):
    return stripe.Account.create(
        business_type=business_type,
        controller={
            "stripe_dashboard": {
                "type": "express",
            },
            "fees": {"payer": "application"},
            "losses": {"payments": "application"},
        },
        country="GB",
    )


def create_stripe_account_session(connected_account_id: str):
    return stripe.AccountSession.create(
        account=connected_account_id,
        components={
            "account_onboarding": {"enabled": True},
        },
    )


def create_stripe_item_checkout_session(item_listing: ItemListing, tag_id: str):
    metadata = {
        "purchase": "item",
        "item_id": item_listing.item_details.id,
        "item_listing_id": item_listing.id,
        "member_id": item_listing.owner.id,
        "store_id": item_listing.store.id,
        "amount": item_listing.listing_price,
        "store_amount": item_listing.store_commission_amount,
        "member_earnings": item_listing.member_earnings,
        "transaction_fee": item_listing.transaction_fee,
    }
    return stripe.checkout.Session.create(
        ui_mode="embedded",
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {"name": item_listing.item_details.name},
                    "unit_amount": to_stripe_amount(item_listing.listing_price),
                },
                "quantity": 1,
            },
        ],
        payment_intent_data={"metadata": metadata},
        mode="payment",
        return_url=f"{settings.FRONTEND_URL}/listing/{tag_id}/return?session_id={{CHECKOUT_SESSION_ID}}",
        metadata=metadata,
    )


def create_stripe_supplies_checkout_session(line_items: list[Dict[str, str]], store_id: str):
    metadata = {"purchase": "supplies", "store_id": store_id, "line_items": line_items}
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        payment_intent_data={"metadata": metadata},
        metadata=metadata,
        return_url=f"{settings.FRONTEND_URL}/store/supplies/return?session_id={{CHECKOUT_SESSION_ID}}",
    )