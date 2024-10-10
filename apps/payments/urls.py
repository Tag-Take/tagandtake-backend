from django.urls import path

from apps.payments.views import (
    create_stripe_item_checkout_secssion_view,
    create_stripe_supplies_checkout_session_view,
    get_stripe_session_status_view,
    get_stripe_session_status_view,
    account_status_view,
    create_onboarding_session_view,
    create_management_session_view,
    create_payouts_session_view,
    create_payments_session_view,
    fetch_notifications_view,
)
from apps.payments.webhooks import (
    stripe_connect_event_webhook,
    stripe_platform_event_webhook,
)

from apps.payments.legacy_views.views import PurchaseTagsView


urlpatterns = [
    path(
        "stripe/account-status/",
        account_status_view,
        name="stripe-account-status",
    ),
    path(
        "stripe/create-onboarding-session/",
        create_onboarding_session_view,
        name="stripe-create-onboarding-session",
    ),
    path(
        "stripe/create-management-session/",
        create_management_session_view,
        name="stripe-create-management-session",
    ),
    path(
        "stripe/create-payouts-session/",
        create_payouts_session_view,
        name="stripe-create-payouts-session",
    ),
    path(
        "stripe/create-payments-session/",
        create_payments_session_view,
        name="stripe-create-payments-session",
    ),
    path(
        "stripe/notifications-session/",
        fetch_notifications_view,
        name="stripe-fetch-notifications",
    ),
    path(
        "stripe/create-item-checkout-session/",
        create_stripe_item_checkout_secssion_view,
        name="create-stripe-item-checkout-session",
    ),
    path(
        "stripe/supplies-checkout-session/",
        create_stripe_supplies_checkout_session_view,
        name="create-stripe-supplies-checkout-session",
    ),
    path(
        "stripe/checkout-session-status/",
        get_stripe_session_status_view,
        name="stripe-session-status",
    ),
    path(
        "stripe/platform-webhook/",
        stripe_platform_event_webhook,
        name="stripe-platform-webhook",
    ),
    path(
        "stripe/connect-webhook/",
        stripe_connect_event_webhook,
        name="stripe-connect-webhook",
    ),
    # TODO: Remove leggacy endpoints
    path(
        "tags/",
        PurchaseTagsView.as_view(),
        name="purchase-tags",
    ),
]
