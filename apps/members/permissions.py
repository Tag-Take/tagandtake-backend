from rest_framework.permissions import BasePermission


class IsMemberUser(BasePermission):
    """
    Custom permission to only allow store users to access the view.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "member"
