from rest_framework import permissions
from rest_framework import status
from apps.common.utils.responses import create_error_response


class IsTagOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, listing):
        return listing.tag.tag_group.store.user == request.user
    

def check_listing_store_permissions(request, view, instance):
    if not IsTagOwner().has_object_permission(request, view, instance):
        return create_error_response(
            "You do not have permission to modify this item.",
            {},
            status.HTTP_403_FORBIDDEN,
        )
    return None
