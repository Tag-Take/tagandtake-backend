from django.urls import path
from apps.marketplace.views import (
    ListingCreateView,
    ListingRetrieveView,
    ListingRoleCheckView,
    CreateItemAndListingView,
    ReplaceTagView,
    RecallListingView,
    GenerateNewCollectionPinView,
    DelistListing,
    CollectRecalledListingView,
    StoreRecalledListingListView,
)


urlpatterns = [
    path("members/me/listings/", ListingCreateView.as_view(), name="listing-create"),
    path(
        "members/me/item-listings/",
        CreateItemAndListingView.as_view(),
        name="item-listing-create",
    ),
    path(
        "members/me/recalled-listings/<int:id>/generate-collection-pin/",
        GenerateNewCollectionPinView.as_view(),
        name="generate-collection-pin",
    ),
    path(
        "stores/me/recalled-listings/",
        StoreRecalledListingListView.as_view(),
        name="store-recalled-listing-retrieve",
    ),
    path(
        "stores/me/listings/<int:id>/replace-tag/",
        ReplaceTagView.as_view(),
        name="listing-replace-tag",
    ),
    path(
        "stores/me/listings/<int:id>/recall/",
        RecallListingView.as_view(),
        name="listing-recall",
    ),
    path(
        "stores/me/listings/<int:id>/delist/",
        DelistListing.as_view(),
        name="listing-delist",
    ),
    path(
        "stores/me/recalled-listings/<int:id>/collect/",
        CollectRecalledListingView.as_view(),
        name="recalled-listing-collect",
    ),
    path("listings/<int:id>/", ListingRetrieveView.as_view(), name="listing-retrieve"),
    path(
        "listings/<int:id>/check-role/",
        ListingRoleCheckView.as_view(),
        name="listing-role-check",
    ),
]
