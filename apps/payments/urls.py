from django.urls import path

from apps.payments.views import (
    create_stripe_account_view,
    create_stripe_account_session_view,
    create_stripe_item_checkout_secssion_view,
    create_stripe_supplies_checkout_session_view,
    get_stripe_session_status_view,
)
from apps.payments.webhooks import (
    stripe_connect_event_webhook,
    stripe_platform_event_webhook,
)

from apps.payments.legacy_views.views import PurchaseTagsView


urlpatterns = [
    path(
        "create-stripe-account/",
        create_stripe_account_view,
        name="create-member-stripe-account",
    ),
    path(
        "create-stripe-account-session/",
        create_stripe_account_session_view,
        name="create-stripe-account-session",
    ),
    path(
        "create-stripe-item-checkout-session/",
        create_stripe_item_checkout_secssion_view,
        name="create-stripe-item-checkout-session",
    ),
    path(
        "create-stripe-supplies-checkout-session/",
        create_stripe_supplies_checkout_session_view,
        name="create-stripe-supplies-checkout-session",
    ),
    path(
        "stripe-session-status/",
        get_stripe_session_status_view,
        name="stripe-session-status",
    ),
    path(
        "stripe-platform-webhook/",
        stripe_platform_event_webhook,
        name="stripe-platform-webhook",
    ),
    path(
        "stripe-connect-webhook/",
        stripe_connect_event_webhook,
        name="stripe-connect-webhook",
    ),
    path(
        "tags/",
        PurchaseTagsView.as_view(),
        name="purchase-tags",
    ),
]
