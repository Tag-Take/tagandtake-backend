import stripe

from rest_framework import status
from rest_framework.request import Request
from rest_framework.decorators import api_view

from apps.common.responses import create_success_response, create_error_response
from apps.stores.models import StoreProfile as Store
from apps.marketplace.services.listing_services import ItemListingService
from apps.payments.services.stripe_services import (
    create_stripe_account,
    create_stripe_account_session,
    create_stripe_item_checkout_session,
    create_stripe_supplies_checkout_session,
)
from apps.payments.services.checkout_services import CheckoutSessionService
from apps.payments.serializers import SuppliesCheckoutSessionSerializer
from apps.common.constants import (
    BUSINESS_TYPE,
    ACCOUNT,
    TAG_ID,
    STATUS,
    CLIENT_SECRET,
    SESSION_ID,
    ACCOUNT_SESSION,
)


@api_view(["POST"])
def create_stripe_account_view(request: Request):
    try:
        business_type = request.query_params.get(BUSINESS_TYPE)

        if not business_type:
            return create_error_response(
                "query param 'business_type' is required.",
                {"error": "No business type provided."},
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            account = create_stripe_account()
            return create_success_response(
                "Stripe account created successfully.",
                {ACCOUNT: account.id},
                status.HTTP_200_OK,
            )

        except Exception as e:
            return create_error_response(
                "An error occurred when calling the Stripe API to create an account: ",
                {str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    except:
        return create_error_response(
            "An error occurred when creating the Stripe account: ",
            {str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def create_stripe_account_session_view(request: Request):
    try:
        connected_account_id = request.data.get(ACCOUNT)

        account_session = create_stripe_account_session(connected_account_id)

        return create_success_response(
            "Stripe account session created successfully.",
            {ACCOUNT_SESSION: account_session.id},
            status.HTTP_200_OK,
        )

    except Exception as e:
        return create_error_response(
            "An error occurred when creating the Stripe account session: ",
            {str(e)},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
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

        session = create_stripe_item_checkout_session(item_listing, tag_id)

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


# TODO: Add permissions
# @permission_classes([permissions.IsAuthenticated])  # Add IsStoreUser if necessary
@api_view(["POST"])
def create_stripe_supplies_checkout_session_view(request: Request):
    user = request.user
    if user.is_anonymous:
        store_id = 1
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
            session = create_stripe_supplies_checkout_session(line_items, store_id)

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
