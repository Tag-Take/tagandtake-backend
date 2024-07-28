from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.accounts.urls import urlpatterns as account_urls
from apps.stores.urls import urlpatterns as store_urls
from apps.members.urls import urlpatterns as member_urls
from apps.items.urls import urlpatterns as item_urls
from apps.payments.urls import urlpatterns as payment_urls

API_VERSION = "v1"

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # API Endpoints
    path(f"api/{API_VERSION}/accounts/", include(account_urls)),
    path(f"api/{API_VERSION}/stores/", include(store_urls)),
    path(f"api/{API_VERSION}/members/", include(member_urls)),
    path(f"api/{API_VERSION}/", include(item_urls)),
    path(f"api/{API_VERSION}/payments/", include(payment_urls)),
]
