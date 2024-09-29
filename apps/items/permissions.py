from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.common.responses import create_error_response
from apps.items.models import Item


class IsItemOwner(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, item: Item):
        return item.owner_user == request.user


def check_item_permissions(request: Request, view: APIView, item: Item):
    if not request.user.is_authenticated:
        return create_error_response(
            "Authentication required.", {}, status.HTTP_401_UNAUTHORIZED
        )
    if not IsItemOwner().has_object_permission(request, view, item):
        return create_error_response(
            "You do not have permission to modify this item.",
            {},
            status.HTTP_403_FORBIDDEN,
        )
    return None
