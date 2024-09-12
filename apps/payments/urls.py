from django.urls import path

from apps.payments.views.legacy.views import (
    create_stripe_account,
    create_stripe_account_session,
    PurchaseTagsView,
    PurchaseListingView,
)
from apps.payments.views.webhooks import stripe_connect_event_webhook, stripe_platform_event_webhook


urlpatterns = [
    path("create-stripe-account/", create_stripe_account, name="create-stripe-account"),
    path(
        "create-account-session/",
        create_stripe_account_session,
        name="create-account-session",
    ),
    path("tags/", PurchaseTagsView.as_view(), name="purchase-tags"),
    path(
        "listings/<int:tag_id>/", PurchaseListingView.as_view(), name="purchase-listing"
    ),
    path(
        "stripe-platform-webhook/",
        stripe_platform_event_webhook,
        name="stripe-platform-webhook",
    ),
    path(
        "stripe-connect-webhook/", stripe_connect_event_webhook, name="stripe-connect-webhook"
    ),
]
