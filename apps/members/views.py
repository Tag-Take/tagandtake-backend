from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
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
    permission_classes = [IsAuthenticated, IsMemberUser]
    serializer_class = MemberProfileSerializer

    def get_object(self):
        return self.request.user.member


class MemberNotificationPreferencesView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsMemberUser]
    serializer_class = MemberNotificationPreferencesSerializer

    def get_object(self):
        return MemberNotificationPreferences.objects.get(member=self.request.user.member)


class MemberProfileImageView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsMemberUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  
    serializer_class = MemberProfileImageSerializer

    def get_object(self):
        return self.request.user.member
    
    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(member=self.get_object())

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={})
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(serializer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, serializer):
        serializer.save()
