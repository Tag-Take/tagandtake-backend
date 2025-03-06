from django.urls import path
from apps.stores.views import (
    StoreProfileView,
    GenerateNewPinView,
    StoreOwnerCategoriesView,
    StoreOwnerConditionsView,
    PublicStoreItemCategoriesView,
    PublicStoreItemConditionsView,
    StoreNotificationPreferencesView,
    StoreProfileImageView,
    tags_purchase,
)

urlpatterns = [
    path(
        "stores/me/profile/",
        StoreProfileView.as_view(),
        name="retrieve_update_store_profile",
    ),
    path(
        "stores/me/pin/", GenerateNewPinView.as_view(), name="update_store_profile_pin"
    ),
    path(
        "stores/me/categories/",
        StoreOwnerCategoriesView.as_view(),
        name="store_owner_categories",
    ),
    path(
        "stores/me/conditions/",
        StoreOwnerConditionsView.as_view(),
        name="store_owner_conditions",
    ),
    path(
        "stores/<int:store_id>/categories/",
        PublicStoreItemCategoriesView.as_view(),
        name="public_store_item_categories",
    ),
    path(
        "stores/<int:store_id>/conditions/",
        PublicStoreItemConditionsView.as_view(),
        name="public_store_item_conditions",
    ),
    path(
        "stores/me/notification-settings/",
        StoreNotificationPreferencesView.as_view(),
        name="store_notification_settings",
    ),
    path(
        "stores/me/profile-photo/",
        StoreProfileImageView.as_view(),
        name="store_profile_photo",
    ),
    path(
        "stores/me/purchase-tags/",
        tags_purchase,
        name="purchase_tags",
    ),
]
