from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from apps.common.responses import create_error_response
from apps.marketplace.models import BaseItemListing


class IsTagOwner(permissions.BasePermission):
    def has_object_permission(self, request, view: APIView, listing: BaseItemListing):
        return listing.tag.tag_group.store.user == request.user


class IsListingOwner(permissions.BasePermission):
    def has_object_permission(self, request, view: APIView, listing: BaseItemListing):
        return listing.item.owner_user == request.user


class IsHostStoreOwner(permissions.BasePermission):
    def has_object_permission(self, request, view: APIView, listing: BaseItemListing):
        tag_id = view.kwargs.get("tag_id")
        return listing.tag.tag_group.store.user == request.user


def check_listing_store_permissions(request, view: APIView, listing: BaseItemListing):
    if not IsTagOwner().has_object_permission(request, view, listing):
        return create_error_response(
            "You do not have permission to modify this listing.",
            {},
            status.HTTP_403_FORBIDDEN,
        )
    return None


def check_listing_member_permissions(request, view: APIView, listing: BaseItemListing):
    if not listing.item.owner.user.id == request.user.id:
        return create_error_response(
            "You do not have permission to modify this listing.",
            {},
            status.HTTP_403_FORBIDDEN,
        )
