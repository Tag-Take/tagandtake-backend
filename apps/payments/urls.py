from django.urls import path

from apps.payments.views import PurchaseTagsView, PurchaseListingView

urlpatterns = [
    path("tags/", PurchaseTagsView.as_view(), name="purchase-tags"),
    path(
        "listings/<int:tag_id>/", PurchaseListingView.as_view(), name="purchase-listing"
    ),
]
