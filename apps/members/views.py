from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from apps.members.models import MemberProfile, MemberNotificationPreferences
from apps.members.serializers import MemberProfileSerializer, MemberNotificationPreferencesSerializer
from apps.members.permissions import IsMemberUser
from apps.common.s3.constants import PROFILE_PHOTO
from apps.common.s3.utils import upload_file_to_s3, generate_s3_url, get_s3_client, generate_member_profile_folder_name


class MemberProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = MemberProfileSerializer

    def get_object(self):
        user = self.request.user
        try:
            return MemberProfile.objects.get(user=user)
        except MemberProfile.DoesNotExist:
            raise PermissionDenied("Profile not found.")

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = MemberProfileSerializer(profile)
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
        serializer = MemberProfileSerializer(profile, data=request.data, partial=True)
        
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


class MemberNotificationPreferencesView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = MemberNotificationPreferencesSerializer

    def get_object(self):
        user = self.request.user
        try:
            return MemberNotificationPreferences.objects.get(member__user=user)
        except MemberNotificationPreferences.DoesNotExist:
            raise PermissionDenied("Notification preferences not found.")

    def update(self, request, *args, **kwargs):
        preferences = self.get_object()
        serializer = MemberNotificationPreferencesSerializer(preferences, data=request.data, partial=True)
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
    

class MemberProfileImageView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            profile = MemberProfile.objects.get(user=request.user)
        except MemberProfile.DoesNotExist:
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

        folder_name = generate_member_profile_folder_name(profile.id)
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
            profile = MemberProfile.objects.get(user=request.user)
        except MemberProfile.DoesNotExist:
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

        folder_name = generate_member_profile_folder_name(profile.id)
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


