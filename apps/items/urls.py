from django.urls import path

from apps.items.views import (
    MemberItemListCreateView,
    MemberItemRetrieveUpdateDeleteView,
    ItemCategoryListView,
    ItemConditionListView,
)

urlpatterns = [
    path("members/me/items/", MemberItemListCreateView.as_view(), name="create_item"),
    path(
        "members/me/items/<int:pk>/",
        MemberItemRetrieveUpdateDeleteView.as_view(),
        name="item_detail",
    ),
    path(
        "items/categories/", ItemCategoryListView.as_view(), name="item_category_list"
    ),
    path(
        "items/conditions/", ItemConditionListView.as_view(), name="item_condition_list"
    ),
]
