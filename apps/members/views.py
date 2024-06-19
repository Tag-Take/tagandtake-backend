from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from apps.members.models import MemberProfile
from apps.members.serializers import MemberProfileSerializer

class RetrieveMemberProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MemberProfileSerializer

    def get_object(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'member':
            try:
                return MemberProfile.objects.get(user=user)
            except MemberProfile.DoesNotExist:
                raise PermissionDenied("Profile not found.")
        else:
            raise PermissionDenied("You do not have permission to access this profile.")

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile:
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
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Profile not found or user is not activated.",
                    "data": None,
                    "errors": {},
                },
                status=status.HTTP_403_FORBIDDEN,
            )

