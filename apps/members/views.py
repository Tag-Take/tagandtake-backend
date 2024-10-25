from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from apps.members.permissions import IsMemberUser
from apps.members.models import MemberNotificationPreferences
from apps.members.serializers import (
    MemberProfileSerializer,
    MemberNotificationPreferencesSerializer,
    MemberProfileImageSerializer,
)
from apps.common.constants import PROFILE_PHOTO_URL


class MemberProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = MemberProfileSerializer

    def get_object(self):
        return self.request.user.member


class MemberNotificationPreferencesView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = MemberNotificationPreferencesSerializer

    def get_object(self):
        return MemberNotificationPreferences.objects.get(member=self.request.user.member)


class MemberProfileImageView(APIView):
    permission_classes = [IsAuthenticated, IsMemberUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = MemberProfileImageSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            member = serializer.save()
            return Response(
                {PROFILE_PHOTO_URL: member.profile_photo_url}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        serializer = MemberProfileImageSerializer(data={}, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
