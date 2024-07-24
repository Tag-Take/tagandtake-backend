from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from apps.members.models import MemberProfile
from apps.members.serializers import MemberProfileSerializer
from apps.members.permissions import IsMemberUser


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

# All the views needed for users in the marketplace to manage their profile and related data (CRUD)

# Get a user's profile
# GET /api/members/profile/

# Update a user's profile
# PUT /api/members/profile/

# Get a user's stripe account
# GET /api/members/stripe/

# Update a user's stripe account    
# PUT /api/members/stripe/

