from django.urls import path
from apps.marketplace.views import ListingCreateView, ListingRetrieveView

urlpatterns = [
    path('listings/create/', ListingCreateView.as_view(), name='listing-create'),
    path('listings/<int:id>/', ListingRetrieveView.as_view(), name='listing-retrieve'),
]
