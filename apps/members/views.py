from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from apps.common.utils.responses import create_error_response, create_success_response
from apps.accounts.models import User
from apps.members.permissions import IsMemberUser
from apps.members.models import MemberProfile, MemberNotificationPreferences
from apps.members.serializers import (
    MemberProfileSerializer,
    MemberNotificationPreferencesSerializer,
    MemberProfileImageUploadSerializer,
    MemberProfileImageDeleteSerializer,
)


class MemberProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = MemberProfileSerializer

    def get_object(self):
        user: User = self.request.user
        try:
            return MemberProfile.objects.get(user=user)
        except MemberProfile.DoesNotExist:
            raise PermissionDenied("Profile not found.")

    def retrieve(self, request: Request, *args, **kwargs):
        member: MemberProfile = self.get_object()
        serializer = MemberProfileSerializer(member)
        return create_success_response(
            "Profile retrieved successfully.", serializer.data, status.HTTP_200_OK
        )

    def update(self, request: Request, *args, **kwargs):
        member: MemberProfile = self.get_object()
        serializer = MemberProfileSerializer(member, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return create_success_response(
                "Profile updated successfully.", serializer.data, status.HTTP_200_OK
            )
        return create_error_response(
            "Profile update failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
        )


class MemberNotificationPreferencesView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = MemberNotificationPreferencesSerializer

    def get_object(self):
        user = self.request.user
        try:
            return MemberNotificationPreferences.objects.get(member__user=user)
        except MemberNotificationPreferences.DoesNotExist:
            raise PermissionDenied("Notification preferences not found.")

    def retrieve(self, request, *args, **kwargs):
        preferences: MemberNotificationPreferences = self.get_object()
        serializer = MemberNotificationPreferencesSerializer(preferences)
        return create_success_response(
            "Notification preferences retrieved successfully.",
            serializer.data,
            status.HTTP_200_OK,
        )

    def update(self, request: Request, *args, **kwargs):
        preferences: MemberNotificationPreferences = self.get_object()
        serializer = MemberNotificationPreferencesSerializer(
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


class MemberProfileImageView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]

    def dispatch(self, request: Request, *args, **kwargs):
        if request.method == "POST":
            self.parser_classes = [MultiPartParser, FormParser]
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: Request, *args, **kwargs):
        serializer = MemberProfileImageUploadSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            member: MemberProfile = serializer.save()
            try:
                return create_success_response(
                    "Profile photo uploaded successfully.",
                    {"profile_photo_url": member.profile_photo_url},
                    status.HTTP_200_OK,
                )
            except Exception as e:
                return create_error_response(
                    f"Failed to upload profile photo: {str(e)}",
                    {},
                    status.HTTP_400_BAD_REQUEST,
                )
        return create_error_response(
            "Profile photo upload failed.",
            serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request: Request, *args, **kwargs):
        serializer = MemberProfileImageDeleteSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return create_success_response(
                "Profile photo deleted successfully.", {}, status.HTTP_200_OK
            )
        return create_error_response(
            "Profile photo delete failed.",
            serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )
