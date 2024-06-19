from django.contrib import admin
from django.urls import path, include
from apps.accounts.urls import urlpatterns as account_urls
from apps.stores.urls import urlpatterns as store_urls
from apps.members.urls import urlpatterns as member_urls

API_VERSION = "v1"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"api/{API_VERSION}/", include(account_urls)),
    path(f"api/{API_VERSION}/", include(store_urls)),
    path(f"api/{API_VERSION}/", include(member_urls)),
]
