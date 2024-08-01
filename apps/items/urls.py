from django.urls import path

from apps.items.views import (
    ItemCreateView,
    ItemDetailView,
    MemberItemListView,
    ItemCategoryListView,
    ItemConditionListView,
)

urlpatterns = [
    path(
        "create/",
        ItemCreateView.as_view(),
        name="create_item",
    ),
    path(
        "<int:pk>/",
        ItemDetailView.as_view(),
        name="item_detail",
    ),
    path(
        "members/<int:pk>/",
        MemberItemListView.as_view(),
        name="member_item_list",
    ),
    path(
        "categories/",
        ItemCategoryListView.as_view(),
        name="item_category_list",
    ),
    path(
        "conditions/",
        ItemConditionListView.as_view(),
        name="item_condition_list",
    ),
]
