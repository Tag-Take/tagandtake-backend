from django.urls import path
from apps.members.views import (
    MemberProfileView,
    MemberNotificationPreferencesView,
    MemberProfileImageView,
)

urlpatterns = [
    path("members/me/profile/", MemberProfileView.as_view(), name="retrieve_update_member_profile"),
    path("members/me/notification-settings/", MemberNotificationPreferencesView.as_view(), name="notification_settings"),
    path("members/me/profile-photo/", MemberProfileImageView.as_view(), name="profile_photo"),
]
