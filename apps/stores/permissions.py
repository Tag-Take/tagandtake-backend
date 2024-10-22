from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from apps.accounts.models import User
from apps.stores.models import StoreProfile as Store
from apps.common.constants import PIN


class IsStoreUser(BasePermission):
    def has_permission(self, request: Request, view: APIView):
        return request.user.is_authenticated and request.user.role == User.Roles.STORE


class IsStoreWithValidPIN(BasePermission):
    def has_permission(self, request: Request, view: APIView):
        if request.method not in ["PUT", "PATCH", "DELETE"]:
            return True

        store = Store.objects.get(user=request.user)
        pin = request.data.get(PIN)

        if not pin:
            raise ValidationError({"detail": "PIN is required."})

        if not store.validate_pin(pin):
            raise ValidationError({"detail": "Invalid PIN."})

        return True
