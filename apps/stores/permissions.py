from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from apps.accounts.models import User
from apps.stores.models import StoreProfile as Store
from apps.common.constants import PIN, DETAIL


class IsStoreUser(BasePermission):
    def has_permission(self, request: Request, view: APIView):
        return request.user.is_authenticated and request.user.role == User.Roles.STORE


class IsStoreWithValidPIN(BasePermission):
    def has_permission(self, request: Request, view: APIView):
        if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
            return True

        pin = request.data.get(PIN)
        store: Store = request.user.store

        if not pin:
            raise ValidationError({DETAIL: "PIN is required."})

        if not store.validate_pin(pin):
            raise ValidationError({DETAIL: "Invalid PIN."})

        return True
