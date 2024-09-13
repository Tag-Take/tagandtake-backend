import stripe

from django.conf import settings

from rest_framework import status
from rest_framework.request import Request
from rest_framework.decorators import api_view

from apps.common.utils.responses import create_success_response, create_error_response


stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(["POST"])
def create_stripe_account(request: Request):
    try:
        account = stripe.Account.create(
            business_type="individual",
            controller={
                "stripe_dashboard": {
                    "type": "express",
                },
                "fees": {"payer": "application"},
                "losses": {"payments": "application"},
            },
        )
        return create_success_response(
            "Stripe account created successfully.",
            {
                "account": account.id
            },
            status.HTTP_200_OK,
            )
    
    except Exception as e:
        return create_error_response(
            "An error occurred when calling the Stripe API to create an account: ",
            {str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def create_stripe_account_session(request: Request):
    try:
        connected_account_id = request.data.get("account")

        account_session = stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "account_onboarding": {"enabled": True},
            },
        )

        return create_success_response(
            "Stripe account session created successfully.",
            {   
                "client_secret": account_session.client_secret
            },
            status.HTTP_200_OK
        )
    
    except Exception as e:
        return create_error_response(
            "An error occurred when calling the Stripe API to create an account session: ",
            {str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def create_stripe_checkout_session(request: Request):

    stripe.checkout.Session.create(
    line_items=[
        {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Restaurant delivery service"},
            "unit_amount": 10000,
        },
        "quantity": 1,
        },
    ],
    payment_intent_data={"transfer_group": "ORDER100"},
    mode="payment",
    ui_mode="embedded",
    return_url="https://example.com/return?session_id={CHECKOUT_SESSION_ID}",
    )