from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from apps.accounts.models import User


class IsMemberUser(BasePermission):
    def has_permission(self, request: Request, view: APIView):
        return request.user.is_authenticated and request.user.role == User.Roles.MEMBER
