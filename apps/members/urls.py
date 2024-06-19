from django.urls import path
from apps.members.views import RetrieveMemberProfileView

urlpatterns = [
    path("member-profile/", RetrieveMemberProfileView.as_view(), name="retrieve_member_profile"),
]
