from django.urls import path
from apps.stores.views import RetrieveStoreProfileView

urlpatterns = [
    path(
        "profile/",
        RetrieveStoreProfileView.as_view(),
        name="retrieve_store_profile",
    ),
]
