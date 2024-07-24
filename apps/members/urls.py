from django.urls import path
from apps.members.views import MemberProfileView

urlpatterns = [
    path(
        "profile/",
        MemberProfileView.as_view(),
        name="retrieve_member_profile",
    ),
]
