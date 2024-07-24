from django.urls import path
from apps.stores.views import (
    StoreProfileView,
    GenerateNewPinView,
    StoreItemCategoriesView,
    StoreItemConditionsView,
    StoreNotificationPreferencesView,
    StoreProfileImageView
)

urlpatterns = [
    path(
        "profile/",
        StoreProfileView.as_view(),
        name="retrieve_store_profile",
    ),
    path(
        "profile/update-pin/",
        GenerateNewPinView.as_view(),
        name="update_store_profile_pin",
    ),
    path(
        "<int:store_id>/item-categories/",
        StoreItemCategoriesView.as_view(),
        name="store-item-categories",
    ),
    path(
        "<int:store_id>/item-conditions/",
        StoreItemConditionsView.as_view(),
        name="store-item-conditions",
    ),
    path(
        "profile/notifications/",
        StoreNotificationPreferencesView.as_view(),
        name="store-notification-preferences",
    ),
    path('profile/profile-photo/', 
         StoreProfileImageView.as_view(), 
         name='profile-photo'
    ),

]
