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


urlpatterns = [
    path("stripe/account-status/", account_status_view, name="stripe-account-status"),
    path("stripe/onboarding-session/", create_onboarding_session_view, name="stripe-onboarding-session"),
    path("stripe/management-session/", create_management_session_view, name="stripe-management-session"),
    path("stripe/payouts-session/", create_payouts_session_view, name="stripe-payouts-session"),
    path("stripe/payments-session/", create_payments_session_view, name="stripe-payments-session"),
    path("stripe/notifications-session/", fetch_notifications_view, name="stripe-notifications-session"),
    path("stripe/item-checkout-session/", create_stripe_item_checkout_secssion_view, name="stripe-item-checkout-session"),
    path("stripe/supplies-checkout-session/", create_stripe_supplies_checkout_session_view, name="stripe-supplies-checkout-session"),
    path("stripe/checkout-session-status/", get_stripe_session_status_view, name="stripe-session-status"),
    path("stripe/platform-webhook/", stripe_platform_event_webhook, name="stripe-platform-webhook"),
    path("stripe/connect-webhook/", stripe_connect_event_webhook, name="stripe-connect-webhook"),
]
