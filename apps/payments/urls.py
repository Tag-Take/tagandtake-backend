from django.urls import path

from apps.payments.views import PurchaseTagsView

urlpatterns = [
    path("tags/", PurchaseTagsView.as_view(), name="purchase-tags"),
]
