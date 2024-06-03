from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.serializers import UserRegistrationSerializer
from apps.core.services import UserService

class UserSignupView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = UserService.register_user(
                **serializer.validated_data
            )
            response_data = {
                'message': 'User registered successfully. Please check your email to verify your account.',
                'user': {
                    'email': user.email,
                    'username': user.username,
                    'is_store': user.is_store,
                    'is_member': user.is_member,
                    'created_at': user.created_at,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
