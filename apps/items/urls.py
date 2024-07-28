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
        "items/",
        ItemCreateView.as_view(),
        name="create_item",
    ),
    path(
        "items/<int:pk>/",
        ItemDetailView.as_view(),
        name="item_detail",
    ),
    path(
        "members/<int:pk>/items/",
        MemberItemListView.as_view(),
        name="member_item_list",
    ),
    path(
        "items/categories/",
        ItemCategoryListView.as_view(),
        name="item_category_list",
    ),
    path(
        "items/conditions/",
        ItemConditionListView.as_view(),
        name="item_condition_list",
    ),
]
