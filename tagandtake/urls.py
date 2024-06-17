from django.contrib import admin
from django.urls import path, include
from apps.accounts.urls import urlpatterns as account_urls

API_VERSION = "v1"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"api/{API_VERSION}/", include(account_urls)),
]
