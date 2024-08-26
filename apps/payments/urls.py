from django.urls import path

from apps.payments.views import (
    # create_stripe_account,
    # create_account_session,
    PurchaseTagsView, 
    PurchaseListingView
)


urlpatterns = [
    # path("create-stripe-account/", create_stripe_account, name="create-stripe-account"),
    # path("create-account-session/", create_account_session, name="create-account-session"),
    path("tags/", PurchaseTagsView.as_view(), name="purchase-tags"),
    path(
        "listings/<int:tag_id>/", PurchaseListingView.as_view(), name="purchase-listing"
    ),
]
