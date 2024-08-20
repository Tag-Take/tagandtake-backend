from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.common.utils.responses import create_error_response, create_success_response
from apps.stores.utils import generate_pin
from apps.stores.permissions import IsStoreUser
from apps.stores.models import (
    StoreProfile,
    StoreItemCategorie,
    StoreItemConditions,
    StoreNotificationPreferences,
)
from apps.stores.serializers import (
    StoreProfileSerializer,
    StoreItemCategoryUpdateSerializer,
    StoreItemCategorySerializer,
    StoreItemConditionSerializer,
    StoreItemConditionUpdateSerializer,
    StoreNotificationPreferencesSerializer,
    StoreProfileImageDeleteSerializer,
    StoreProfileImageUploadSerializer,
)
from apps.emails.services.email_senders import StoreEmailSender


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
        return create_success_response(
            "Profile retrieved successfully.", serializer.data, status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        pin = request.data.get("pin")
        if not pin or not profile.validate_pin(pin):
            return create_error_response(
                "Invalid PIN.", {"pin": ["Invalid PIN"]}, status.HTTP_400_BAD_REQUEST
            )

        serializer = StoreProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return create_success_response(
                "Profile updated successfully.", serializer.data, status.HTTP_200_OK
            )
        return create_error_response(
            "Profile update failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
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

        StoreEmailSender(profile).send_reset_pin_email()

        return create_success_response(
            "New PIN generated and sent to your email.", {}, status.HTTP_200_OK
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
        return create_success_response(
            "Categories retrieved successfully.", serializer.data, status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = StoreItemCategoryUpdateSerializer(
            data=request.data,
            context={"store_id": self.kwargs["store_id"], "request": request},
        )
        if serializer.is_valid():
            serializer.update_categories()
            return create_success_response(
                "Categories updated successfully.", {}, status.HTTP_200_OK
            )
        return create_error_response(
            "Categories update failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
        )


class StoreItemConditionsView(generics.ListCreateAPIView):
    serializer_class = StoreItemConditionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsStoreUser()]
        return []

    def get_queryset(self):
        store_id = self.kwargs["store_id"]
        return StoreItemConditions.objects.filter(store_id=store_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return create_success_response(
            "Conditions retrieved successfully.", serializer.data, status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = StoreItemConditionUpdateSerializer(
            data=request.data,
            context={"store_id": self.kwargs["store_id"], "request": request},
        )
        if serializer.is_valid():
            serializer.update_conditions()
            return create_success_response(
                "Conditions updated successfully.", {}, status.HTTP_200_OK
            )
        return create_error_response(
            "Conditions update failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
        )


class StoreNotificationPreferencesView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]
    serializer_class = StoreNotificationPreferencesSerializer

    def get_object(self):
        user = self.request.user
        try:
            return StoreNotificationPreferences.objects.get(store__user=user)
        except StoreNotificationPreferences.DoesNotExist:
            raise PermissionDenied("Notification preferences not found.")

    def update(self, request, *args, **kwargs):
        preferences = self.get_object()
        pin = request.data.get("pin")
        if not pin or not preferences.store.validate_pin(pin):
            return create_error_response(
                "Invalid PIN.", {"pin": ["Invalid PIN"]}, status.HTTP_400_BAD_REQUEST
            )

        serializer = StoreNotificationPreferencesSerializer(
            preferences, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return create_success_response(
                "Notification preferences updated successfully.",
                serializer.data,
                status.HTTP_200_OK,
            )
        return create_error_response(
            "Notification preferences update failed.",
            serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )


class StoreProfileImageView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            self.parser_classes = [MultiPartParser, FormParser]
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = StoreProfileImageUploadSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            profile = serializer.save()
            return create_success_response(
                "Profile photo uploaded successfully.",
                {"profile_photo_url": profile.profile_photo_url},
                status.HTTP_200_OK,
            )
        return create_error_response(
            "Profile photo upload failed.",
            serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        serializer = StoreProfileImageDeleteSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            profile = serializer.save()
            return create_success_response(
                "Profile photo deleted successfully.", {}, status.HTTP_200_OK
            )
        return create_error_response(
            "Profile photo delete failed.",
            serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )
