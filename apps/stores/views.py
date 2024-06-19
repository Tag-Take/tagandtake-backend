from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from apps.stores.models import StoreProfile
from apps.stores.serializers import StoreProfileSerializer
class RetrieveStoreProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StoreProfileSerializer

    def get_object(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'store':
            try:
                return StoreProfile.objects.get(user=user)
            except StoreProfile.DoesNotExist:
                raise PermissionDenied("Profile not found.")
        else:
            raise PermissionDenied("You do not have permission to access this profile.")

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile:
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

