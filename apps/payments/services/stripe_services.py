from django.conf import settings
import stripe
from apps.payments.models.accounts import StorePaymentAccount, MemberPaymentAccount
from apps.marketplace.models import ItemListing
from apps.stores.models import StoreProfile as Store

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


def create_stripe_item_checkout_session(item_listing: ItemListing, tag_id):
    return stripe.checkout.Session.create(
        ui_mode="embedded",
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {"name": item_listing.item.name},
                    "unit_amount": item_listing.listing_price * 100,
                },
                "quantity": 1,
            },
        ],
        mode="payment",
        return_url=f"{settings.FRONTEND_URL}/listing/{tag_id}/return?session_id={{CHECKOUT_SESSION_ID}}",
        metadata={
            "purchase": "item",
            "item_id": item_listing.item.id,
            "item_listing_id": item_listing.id,
            "member_id": item_listing.owner.id,
            "store_id": item_listing.store.id,
            "store_amount": item_listing.store_commission_amount,
            "member_earnings": item_listing.member_earnings,
            "transaction_fee": item_listing.transaction_fee,
        },
    )


def create_stripe_supplies_checkout_session(
    line_items: list[dict],
    store_id: int,
):
    return stripe.checkout.Session.create(
        ui_mode="embedded",
        line_items=line_items,
        mode="payment",
        return_url=f"{settings.FRONTEND_URL}/store/supplies/return?session_id={{CHECKOUT_SESSION_ID}}",
        metadata={
            "purchase": "supplies",
            "store_id": store_id,
        },
    )


def transfer_funds_to_store(event):
    session = event["data"]["object"]
    metadata = event["data"]["object"]["metadata"]

    store_amount = metadata["store_amount"]
    store_id = metadata["store_id"]
    payment_intent_id = session["payment_intent"]

    store_payment_account = StorePaymentAccount(store__id=store_id)
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

    stripe.Transfer.create(
        amount=store_amount,
        currency="gbp",
        source_transaction=payment_intent["latest_charge"],
        destination=store_payment_account.stripe_account_id,
    )


def transfer_funds_to_member(event):
    session = event["data"]["object"]
    metadata = event["data"]["object"]["metadata"]

    member_amount = metadata["member_amount"]
    member_id = metadata["member_id"]
    payment_intent_id = session["payment_intent"]

    member_payment_account = MemberPaymentAccount(member__id=member_id)
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

    stripe.Transfer.create(
        amount=member_amount,
        currency="gbp",
        source_transaction=payment_intent["latest_charge"],
        destination=member_payment_account.stripe_account_id,
    )
