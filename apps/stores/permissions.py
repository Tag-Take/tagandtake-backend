from rest_framework.permissions import BasePermission
from apps.stores.models import StoreProfile


class IsStoreUser(BasePermission):
    """
    Custom permission to only allow store users to access the view.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "store"
