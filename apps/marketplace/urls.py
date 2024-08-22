from django.urls import path
from apps.marketplace.views import (
    ListingCreateView,
    ListingRetrieveView,
    ListingRoleCheckView,
    CreateItemAndListingView,
    ReplaceTagView,
    RecallListingView,
    DelistListing,
    DelistRecalledListingView,
    StoreRecalledListingListView,
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
        "listings/<int:id>/check-role/",
        ListingRoleCheckView.as_view(),
        name="listing-role-check",
    ),
    path(
        "listings/<int:id>/replace-tag/",
        ReplaceTagView.as_view(),
        name="listing-replace-tag",
    ),
    path(
        "recalled-listings/stores/",
        StoreRecalledListingListView.as_view(),
        name="store-recalled-listing-retrieve",
    ),
    path(
        "listings/<int:id>/recall/", RecallListingView.as_view(), name="listing-recall"
    ),
    path("listings/<int:id>/delist/", DelistListing.as_view(), name="listing-delist"),
    path(
        "recalled-listings/<int:id>/delist/",
        DelistRecalledListingView.as_view(),
        name="recalled-listing-delist",
    ),
]
