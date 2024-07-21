from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from apps.stores.models import StoreProfile, StoreItemCategorie, StoreItemConditions
from apps.stores.serializers import (
    StoreProfileSerializer,
    StoreItemCategoryUpdateSerializer,
    StoreItemCategorySerializer,
    StoreItemConditionSerializer, 
    StoreItemConditionUpdateSerializer
)
from apps.stores.permissions import IsStoreUser
from apps.stores.utils import generate_pin, send_rest_pin_email


class StoreProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]
    serializer_class = StoreProfileSerializer

    def get_object(self):
        user = self.request.user
        try:
            return StoreProfile.objects.get(user=user)
        except StoreProfile.DoesNotExist:
            raise PermissionDenied("Profile not found.")

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = StoreProfileSerializer(profile)
        return Response(
            {
                "status": "success",
                "message": "Profile retrieved successfully.",
                "data": serializer.data,
                "errors": {},
            },
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        pin = request.data.get("pin")
        if not pin or not profile.validate_pin(pin):
            return Response(
                {
                    "status": "error",
                    "message": "Invalid PIN.",
                    "data": {},
                    "errors": {"pin": ["Invalid PIN"]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StoreProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Profile updated successfully.",
                    "data": serializer.data,
                    "errors": {},
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Profile update failed.",
                "data": {},
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class GenerateNewPinView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]

    def get_object(self):
        user = self.request.user
        try:
            return StoreProfile.objects.get(user=user)
        except StoreProfile.DoesNotExist:
            raise PermissionDenied("Profile not found.")

    def put(self, request, *args, **kwargs):
        profile = self.get_object()

        profile.pin = generate_pin()
        profile.save()

        send_rest_pin_email(profile)

        return Response(
            {
                "status": "success",
                "message": "New PIN generated and sent to your email.",
                "data": {},
                "errors": {},
            },
            status=status.HTTP_200_OK,
        )


class StoreItemCategoriesView(generics.ListCreateAPIView):
    serializer_class = StoreItemCategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsStoreUser()]
        return []

    def get_queryset(self):
        store_id = self.kwargs["store_id"]
        return StoreItemCategorie.objects.filter(store_id=store_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": "Categories retrieved successfully.",
                "data": serializer.data,
                "errors": {},
            },
            status=status.HTTP_200_OK,
        )
    
    def create(self, request, *args, **kwargs):
        serializer = StoreItemCategoryUpdateSerializer(
            data=request.data,
            context={"store_id": self.kwargs["store_id"], "request": request},
        )
        if serializer.is_valid():
            serializer.update_categories()
            return Response(
                {
                    "status": "success",
                    "message": "Categories updated successfully.",
                    "data": {},
                    "errors": {},
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Categories update failed.",
                "data": {},
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class StoreItemConditionsView(generics.ListCreateAPIView):
    serializer_class = StoreItemConditionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsStoreUser()]
        return []

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        return StoreItemConditions.objects.filter(store_id=store_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": "Conditions retrieved successfully.",
                "data": serializer.data,
                "errors": {},
            },
            status=status.HTTP_200_OK,
        )
    
    def create(self, request, *args, **kwargs):
        serializer = StoreItemConditionUpdateSerializer(data=request.data, context={'store_id': self.kwargs['store_id'], 'request': request})
        if serializer.is_valid():
            serializer.update_conditions()
            return Response(
                {
                    "status": "success",
                    "message": "Conditions updated successfully.",
                    "data": {},
                    "errors": {},
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Conditions update failed.",
                "data": {},
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    


# Retrieve Store Notification Preferences
# GET /api/v1/stores/profile/notifications/
# Update Store Notification Preferences
# PUT /api/v1/stores/profile/notifications/
# PATCH /api/v1/stores/profile/notifications/

# PUT /api/v1/stores/profile/active-tags-count/
# PATCH /api/v1/stores/profile/active-tags-count/
# Fields: active_tags_count
# Update Store Profile (PIN)

# Retrieve Store Payment Details
# PUT /api/v1/stores/profile/payment-details/
# PATCH /api/v1/stores/profile/payment-details/
# Fields: stripe_customer_id, stripe_account_id, commission
# Update Store Profile (Store Settings)

# Retrieve Store Profile Picture
# GET /api/v1/stores/profile/picture/
# Update Store Profile Picture
# PUT /api/v1/stores/profile/picture/
# PATCH /api/v1/stores/profile/picture/
# Delete Store Profile

# DELETE /api/v1/stores/profile/
