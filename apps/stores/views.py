from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from apps.stores.models import (
    StoreProfile, 
    StoreItemCategorie, 
    StoreItemConditions,
    StoreNotificationPreferences
)
from apps.stores.serializers import (
    StoreProfileSerializer,
    StoreItemCategoryUpdateSerializer,
    StoreItemCategorySerializer,
    StoreItemConditionSerializer, 
    StoreItemConditionUpdateSerializer,
    StoreNotificationPreferencesSerializer
)
from apps.stores.permissions import IsStoreUser
from apps.stores.utils import generate_pin, send_rest_pin_email
from apps.common.s3.utils import (
    upload_file_to_s3, get_s3_client, generate_store_profile_folder_name, generate_s3_url
)
from apps.common.s3.constants import PROFILE_PHOTO

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
            return Response(
                {
                    "status": "error",
                    "message": "Invalid PIN.",
                    "data": {},
                    "errors": {"pin": ["Invalid PIN"]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StoreNotificationPreferencesSerializer(preferences, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Notification preferences updated successfully.",
                    "data": serializer.data,
                    "errors": {},
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Notification preferences update failed.",
                "data": {},
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
class StoreProfileImageView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            profile = StoreProfile.objects.get(user=request.user)
        except StoreProfile.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Store profile not found.",
                    "data": {},
                    "errors": {"profile": ["Store profile not found"]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        file = request.FILES.get('profile_photo')
        if not file:
            return Response(
                {
                    "status": "error",
                    "message": "No file uploaded.",
                    "data": {},
                    "errors": {"profile_photo": ["No file uploaded"]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        folder_name = generate_store_profile_folder_name(profile.id)
        key = f'{folder_name}/{PROFILE_PHOTO}.jpg'

        try:
            upload_file_to_s3(file, key)
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                    "data": {},
                    "errors": {"profile_photo": ["Failed to upload profile photo"]},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        presigned_url = generate_s3_url(key)
        profile.profile_photo_url = presigned_url
        profile.save()

        return Response(
            {
                "status": "success",
                "message": "Profile photo uploaded successfully.",
                "data": {
                    "profile_photo_url": presigned_url
                },
                "errors": {},
            },
            status=status.HTTP_200_OK,
        )
    
    def delete(self, request, *args, **kwargs):
        try:
            profile = StoreProfile.objects.get(user=request.user)
        except StoreProfile.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Store profile not found.",
                    "data": {},
                    "errors": {"profile": ["Store profile not found"]},
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not profile.profile_photo_url:
            return Response(
                {
                    "status": "error",
                    "message": "No profile photo to delete.",
                    "data": {},
                    "errors": {"profile_photo": ["No profile photo to delete"]},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        folder_name = generate_store_profile_folder_name(profile.id)
        key = f'{folder_name}/{PROFILE_PHOTO}.jpg'

        s3 = get_s3_client()
        try:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                    "data": {},
                    "errors": {"profile_photo": ["Failed to delete profile photo"]},
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        profile.profile_photo_url = None
        profile.save()

        return Response(
            {
                "status": "success",
                "message": "Profile photo deleted successfully.",
                "data": {},
                "errors": {},
            },
            status=status.HTTP_200_OK,
        )



# Retrieve Store Payment Details
# PUT /api/v1/stores/profile/payment-details/
# PATCH /api/v1/stores/profile/payment-details/
# Fields: stripe_customer_id, stripe_account_id, commission
# Update Store Profile (Store Settings)

# Purchase tag group
# POST /api/v1/stores/purchase-tag-group/

