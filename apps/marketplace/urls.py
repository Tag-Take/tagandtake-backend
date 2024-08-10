from django.urls import path
from apps.marketplace.views import (
    ListingCreateView,
    ListingRetrieveView,
    ListingRoleCheckView,
    CreateItemAndListingView,
    RecallListingView,
    DelistListing,
    DelistRecalledListingView,
)

urlpatterns = [
    path("listings/create/", ListingCreateView.as_view(), name="listing-create"),
    path(
        "listings/item-listing-create/",
        CreateItemAndListingView.as_view(),
        name="item-listing-create",
    ),
    path("listings/<int:id>/", ListingRetrieveView.as_view(), name="listing-retrieve"),
    path(
        "listings/<int:id>/role-check/",
        ListingRoleCheckView.as_view(),
        name="listing-role-check",
    ),
    path(
        "listings/<int:id>/recall/", RecallListingView.as_view(), name="listing-recall"
    ),
    path("listings/<int:id>/delist/", DelistListing.as_view(), name="listing-delist"),
    path(
        "listings/recalled/<int:id>/delist/",
        DelistRecalledListingView.as_view(),
        name="recalled-listing-delist",
    ),
]
