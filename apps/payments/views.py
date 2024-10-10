import stripe

from rest_framework import status
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

from apps.accounts.models import User
from apps.common.responses import create_success_response, create_error_response
from apps.stores.models import StoreProfile as Store
from apps.members.services import MemberService
from apps.stores.services.store_services import StoreService
from apps.marketplace.services.listing_services import ItemListingService
from apps.payments.services.stripe_services import StripeService
from apps.payments.services.checkout_services import CheckoutSessionService
from apps.payments.serializers import SuppliesCheckoutSessionSerializer
from apps.payments.services.account_services import PaymentAccountService
from apps.common.constants import (
    TAG_ID,
    STATUS,
    CLIENT_SECRET,
    SESSION_ID,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@api_view(["GET"])
@permission_classes([IsAuthenticated])  
def account_status_view(request: Request):
    try:
        user = request.user

        payment_account = PaymentAccountService.get_or_create_payment_account(user)

        connected_account_id = payment_account.stripe_account_id

        onboarded = StripeService.is_account_fully_onboarded(connected_account_id)

        return create_success_response(
            "Account status retrieved successfully.",
            {"onboarded": onboarded},
            status.HTTP_200_OK
        )

    except Exception as e:
        return create_error_response(
            "Error retrieving account status",
            {"error": str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def create_onboarding_session_view(request: Request):
    try:
        user = request.user

        # Use the refactored service to get or create the payment account
        payment_account = PaymentAccountService.get_or_create_payment_account(user)

        connected_account_id = payment_account.stripe_account_id

        # Create onboarding session
        session = StripeService.create_stripe_account_onboarding_session(connected_account_id)

        return create_success_response(
            "Onboarding session created successfully.",
            {"client_secret": session.client_secret},
            status.HTTP_200_OK
        )

    except Exception as e:
        return create_error_response(
            "Error creating onboarding session",
            {"error": str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_management_session_view(request: Request):
    try:
        user = request.user

        payment_account = PaymentAccountService.get_or_create_payment_account(user)
        connected_account_id = payment_account.stripe_account_id

        # Create account management session
        session = StripeService.create_stripe_account_management_session(connected_account_id)

        return create_success_response(
            "Management session created successfully.",
            {"client_secret": session.client_secret},
            status.HTTP_200_OK
        )

    except Exception as e:
        return create_error_response(
            "Error creating management session",
            {"error": str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payouts_session_view(request: Request):
    try:
        user = request.user

        # Retrieve payment account using existing service
        payment_account = PaymentAccountService.get_or_create_payment_account(user)
        connected_account_id = payment_account.stripe_account_id

        # Create a session for managing payouts
        session = StripeService.create_stripe_account_balances_session(connected_account_id)

        return create_success_response(
            "Payout session created successfully.",
            {"client_secret": session.client_secret},
            status.HTTP_200_OK
        )

    except Exception as e:
        return create_error_response(
            "Error creating payout session.",
            {"error": str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payments_session_view(request: Request):
    try:
        user = request.user

        # Retrieve payment account using existing service
        payment_account = PaymentAccountService.get_or_create_payment_account(user)
        connected_account_id = payment_account.stripe_account_id

        # Create a session for managing payments
        session = StripeService.create_stripe_account_payments_session(connected_account_id)

        return create_success_response(
            "Payments session created successfully.",
            {"client_secret": session.client_secret},
            status.HTTP_200_OK
        )

    except Exception as e:
        return create_error_response(
            "Error creating payments session.",
            {"error": str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def fetch_notifications_view(request: Request):
    try:
        user = request.user

        # Retrieve payment account using existing service
        payment_account = PaymentAccountService.get_or_create_payment_account(user)
        connected_account_id = payment_account.stripe_account_id

        # Create a session for fetching notifications
        session = StripeService.create_stripe_account_notifications_session(connected_account_id)

        return create_success_response(
            "Notifications session created successfully.",
            {"client_secret": session.client_secret},
            status.HTTP_200_OK
        )

    except Exception as e:
        return create_error_response(
            "Error fetching notifications.",
            {"error": str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(["POST"])
def create_stripe_item_checkout_secssion_view(request: Request):
    try:
        tag_id = request.data.get(TAG_ID)
        item_listing = ItemListingService.get_item_listing_by_tag_id(tag_id)

        if not tag_id:
            return create_error_response(
                "Tag ID is required.",
                {"error": "No Tag ID provided."},
                status.HTTP_400_BAD_REQUEST,
            )

        session = StripeService.create_stripe_item_checkout_session(
            item_listing, tag_id
        )

        CheckoutSessionService.create_item_checkout_session(session, item_listing)

        return create_success_response(
            "Checkout session created successfully.",
            {CLIENT_SECRET: session.client_secret},
            status.HTTP_200_OK,
        )

    except Exception as e:
        return create_error_response(
            "An error occurred when creating the Stripe Checkout Session: ",
            {str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def create_stripe_supplies_checkout_session_view(request: Request):
    user = request.user
    if user.is_anonymous:
        # get first store
        store = Store.objects.first()
        store_id = store.id
    else:
        try:
            store = Store.objects.get(user=user)
            store_id = store.id
        except Store.DoesNotExist:
            return create_error_response(
                "Profile not found.", {}, status.HTTP_404_NOT_FOUND
            )

    serializer = SuppliesCheckoutSessionSerializer(data=request.data)
    if serializer.is_valid():
        line_items = serializer.save()

        try:
            session = StripeService.create_stripe_supplies_checkout_session(
                line_items, store_id
            )

            CheckoutSessionService.create_supplies_checkout_session(
                session, store, line_items
            )

            return create_success_response(
                "Checkout session created successfully.",
                {CLIENT_SECRET: session.client_secret},
                status.HTTP_200_OK,
            )

        except Exception as e:
            return create_error_response(
                "An error occurred when creating the Stripe Checkout Session: ",
                {str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return create_error_response(
        "An error occurred when creating the Stripe Checkout Session: ",
        serializer.errors,
        status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
def get_stripe_session_status_view(request: Request):
    try:
        session_id = request.query_params.get(SESSION_ID)

        if not session_id:
            return create_error_response(
                "query param 'session_id' is required.",
                {"error": "No session ID provided."},
                status.HTTP_400_BAD_REQUEST,
            )

        session = stripe.checkout.Session.retrieve(session_id)

        return create_success_response(
            "Session status retrieved successfully.",
            {
                STATUS: session.status,
            },
            status.HTTP_200_OK,
        )

    except Exception as e:
        return create_error_response(
            "An error occurred when retrieving the session status: ",
            {str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
