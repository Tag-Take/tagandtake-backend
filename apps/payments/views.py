import stripe

from rest_framework import status
from rest_framework.request import Request
from rest_framework.decorators import api_view

from apps.accounts.models import User
from apps.common.responses import create_success_response, create_error_response
from apps.stores.models import StoreProfile as Store
from apps.members.services import MemberService
from apps.stores.services.store_services import StoreService
from apps.marketplace.services.listing_services import ItemListingService
from apps.payments.services.stripe_services import StripeService
from apps.payments.services.checkout_services import CheckoutSessionService
from apps.payments.serializers import SuppliesCheckoutSessionSerializer
from apps.payments.services.account_services import MemberPaymentAccountService, StorePaymentAccountService
from apps.common.constants import (
    TAG_ID,
    STATUS,
    CLIENT_SECRET,
    SESSION_ID,
)

# TODO: Add permissions
@api_view(["POST"])
def manage_stripe_account_view(request: Request):
    if request.user.is_anonymous:
        role = User.Roles.MEMBER
        user = User.objects.first()  # Placeholder for testing
    else:
        user = request.user
        role = user.role

    # Step 1: Get the connected Stripe account ID
    try:
        if role == User.Roles.MEMBER:
            member = MemberService.get_member_by_user(user)
            payment_account = MemberPaymentAccountService.get_or_create_member_payment_account(
                member
            )
        elif role == User.Roles.STORE:
            store = StoreService.get_store_by_user(user)
            payment_account = StorePaymentAccountService.get_or_create_store_payment_account(
                store
            )

        connected_account_id = payment_account.stripe_account_id

        # Step 2: Check the status of the Stripe account to determine session type
        account = stripe.Account.retrieve(connected_account_id)
        if account.details_submitted:
            # Account fully onboarded, create dashboard session
            session = StripeService.create_stripe_account_management_session(
                connected_account_id
            )
            ui = "dashboard"
        else:
            # Onboarding not completed, create onboarding session
            session = StripeService.create_stripe_account_onboarding_session(
                connected_account_id
            )
            pending_transfers = member.pending_transfers if member else store.pending_transfers
            ui = "onboarding"

        return create_success_response(
            f"Stripe account session created successfully. - {ui}",
            {
                "client_secret": session.client_secret,
                "pending_transfers": pending_transfers
            },
            status.HTTP_200_OK,
        )

    except Exception as e:
        return create_error_response(
            "An error occurred when managing the Stripe account: ",
            {str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# TODO: Add permissions
@api_view(["POST"])
def create_payments_session_view(request: Request):
    try:
        user = request.user
        role = user.role

        if role == User.Roles.MEMBER:
            member = MemberService.get_member_by_user(user)
            payment_account = MemberPaymentAccountService.get_member_payment_account(member)
        elif role == User.Roles.STORE:
            store = StoreService.get_store_by_user(user)
            payment_account = StorePaymentAccountService.get_store_payment_account(store)

        connected_account_id = payment_account.stripe_account_id

        # Call the service to create the payments session
        session = StripeService.create_stripe_account_payments_session(connected_account_id)

        return create_success_response(
            "Payments session created successfully.",
            {"client_secret": session.client_secret},
            status.HTTP_200_OK
        )

    except Exception as e:
        return create_error_response(
            "Error creating payments session",
            {"error": str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# TODO: Add permissions
@api_view(["POST"])
def create_payouts_session_view(request: Request):
    try:
        user = request.user
        role = user.role

        if role == User.Roles.MEMBER:
            member = MemberService.get_member_by_user(user)
            payment_account = MemberPaymentAccountService.get_member_payment_account(member)
        elif role == User.Roles.STORE:
            store = StoreService.get_store_by_user(user)
            payment_account = StorePaymentAccountService.get_store_payment_account(store)

        connected_account_id = payment_account.stripe_account_id

        session = StripeService.create_stripe_account_balances_session(connected_account_id)

        return create_success_response(
            "Payouts session created successfully.",
            {"client_secret": session.client_secret},
            status.HTTP_200_OK
        )

    except Exception as e:
        return create_error_response(
            "Error creating payouts session",
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
