from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.accounts.urls import urlpatterns as account_urls
from apps.stores.urls import urlpatterns as store_urls
from apps.members.urls import urlpatterns as member_urls
from apps.items.urls import urlpatterns as item_urls
from apps.payments.urls import urlpatterns as payment_urls
from apps.marketplace.urls import urlpatterns as marketplace_urls

API_VERSION = "v1"

urlpatterns = [
    # Django Admin
    path(f"/admin/", admin.site.urls),
    # API Documentation
    path(f"/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        f"/schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # App Endpoints
    path(f"{API_VERSION}/", include(account_urls)),
    path(f"{API_VERSION}/", include(store_urls)),
    path(f"{API_VERSION}/", include(member_urls)),
    path(f"{API_VERSION}/", include(item_urls)),
    path(f"{API_VERSION}/", include(payment_urls)),
    path(f"{API_VERSION}/", include(marketplace_urls)),
]
