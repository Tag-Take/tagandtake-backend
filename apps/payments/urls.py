from django.urls import path

from apps.payments.views import (
    create_stripe_account_view,
    create_stripe_account_session,
    create_stripe_item_checkout_session,
    create_stripe_supplies_checkout_session,
)
from apps.payments.webhooks import (
    stripe_connect_event_webhook,
    stripe_platform_event_webhook,
)


urlpatterns = [
    path(
        "create-stripe-account/",
        create_stripe_account_view,
        name="create-member-stripe-account",
    ),
    path(
        "create-stripe-account-session/",
        create_stripe_account_session,
        name="create-stripe-account-session",
    ),
    path(
        "create-stripe-item-checkout-session/",
        create_stripe_item_checkout_session,
        name="create-stripe-item-checkout-session",
    ),
    path(
        "create-stripe-supplies-checkout-session/",
        create_stripe_supplies_checkout_session,
        name="create-stripe-supplies-checkout-session",
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
]
