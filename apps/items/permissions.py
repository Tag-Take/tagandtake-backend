from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.items.models import Item


class IsItemOwner(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Item):
        return obj.owner_user == request.user
