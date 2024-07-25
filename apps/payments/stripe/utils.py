# stripe_utils.py
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_connected_account(email):
    try:
        account = stripe.Account.create(
            type="express",
            country="UK",
            email=email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
        )
        return account.id
    except stripe.error.StripeError as e:
        # Handle Stripe error
        raise e
