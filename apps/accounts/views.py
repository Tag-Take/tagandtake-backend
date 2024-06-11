from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import (
    StoreSignUpSerializer,
    MemberSignUpSerializer,
    CustomTokenObtainPairSerializer,
)

from django.contrib.auth import get_user_model


User = get_user_model()


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]  # Allow any user to access this view

    def get_serializer_class(self):
        signup_type = self.request.query_params.get("type")
        if signup_type == "store":
            return StoreSignUpSerializer
        elif signup_type == "member":
            return MemberSignUpSerializer
        else:
            return None

    def create(self, request, *args, **kwargs):
        signup_type = request.query_params.get("type")
        if not signup_type:
            return Response(
                {"error": "Signup type not specified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer_class = self.get_serializer_class()
        if not serializer_class:
            return Response(
                {"error": "Invalid signup type"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": f"{signup_type.capitalize()} user created successfully.",
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            user = None
            try:
                user = User.objects.get(username=request.data.get('username'))
            except User.DoesNotExist:
                pass

            if user is not None and not user.is_active:
                return Response({"detail": "User account is not active."}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"detail": "No active account found with the given credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)