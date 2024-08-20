from django.urls import path
from apps.members.views import (
    MemberProfileView,
    MemberNotificationPreferencesView,
    MemberProfileImageView,
)

urlpatterns = [
    path(
        "profile/",
        MemberProfileView.as_view(),
        name="retrieve_member_profile",
    ),
    path(
        "profile/notifications/",
        MemberNotificationPreferencesView.as_view(),
        name="store-notification-preferences",
    ),
    path(
        "profile/profile-photo/", MemberProfileImageView.as_view(), name="profile-photo"
    ),
]
