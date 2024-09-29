from rest_framework import permissions
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from apps.common.responses import create_error_response
from apps.marketplace.models import BaseItemListing


class IsTagOwner(permissions.BasePermission):
    def has_object_permission(self, request, view: APIView, listing: BaseItemListing):
        return listing.tag.tag_group.store.user == request.user


class PermissionCheckMixin:
    def check_store_permissions(self, request, obj):
        if not check_listing_store_permissions(request, self, obj):
            raise PermissionDenied("You do not have permission to perform this action.")

    def check_member_permissions(self, request, obj):
        if not check_listing_member_permissions(request, self, obj):
            raise PermissionDenied("You do not have permission to perform this action.")


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
