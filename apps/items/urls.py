from django.urls import path

from apps.items.views import (
    ItemCreateView
)

urlpatterns = [
    path(
        "",
        ItemCreateView.as_view(),
        name="create_item",
    ),
]