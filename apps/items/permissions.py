from rest_framework import permissions
from rest_framework import status
from apps.members.permissions import IsMemberUser
from apps.common.utils.responses import create_error_response


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


def check_item_permissions(request, view, instance):
    if not request.user.is_authenticated:
        return create_error_response(
            "Authentication required.", {}, status.HTTP_401_UNAUTHORIZED
        )
    if not IsOwner().has_object_permission(request, view, instance):
        return create_error_response(
            "You do not have permission to modify this item.",
            {},
            status.HTTP_403_FORBIDDEN,
        )
    return None
