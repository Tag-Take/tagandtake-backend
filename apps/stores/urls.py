from django.urls import path
from apps.stores.views import RetrieveStoreProfileView

urlpatterns = [
    path("store-profile/", RetrieveStoreProfileView.as_view(), name="retrieve_store_profile"),
]
