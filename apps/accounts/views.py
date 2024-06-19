from datetime import datetime

from django.http import QueryDict
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.timezone import now
from django.contrib.auth.tokens import default_token_generator

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.serializers import (
    SignUpSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from apps.accounts.utils import generate_activation_context
from apps.notifications.utils import send_email
from apps.accounts.signals import user_activated

User = get_user_model()


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        signup_type = request.query_params.get("type")
        request.data["role"] = signup_type
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "status": "success",
                    "message": f"{signup_type.capitalize()} user created successfully.",
                    "data": {"user": serializer.data},
                    "errors": {},
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "User creation failed.",
                    "data": None,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ActivateUserView(APIView):
    authentication_classes = []

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            user_activated.send(sender=user.__class__, instance=user)
            return Response(
                {
                    "status": "success",
                    "message": "Account activated successfully",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Activation link is invalid",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResendActivationEmailView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {"status": "error", "message": "User is already active."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                context = generate_activation_context(user)
                send_email(
                    subject="Activate your account",
                    to=user.email,
                    template_name="./activation_email.html",
                    context=context,
                )
                return Response(
                    {"status": "success", "message": "Activation email sent."},
                    status=status.HTTP_200_OK,
                )
        except User.DoesNotExist:
            return Response(
                {"status": "error", "message": "No user associated with this email."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {
                    "status": "error",
                    "message": "Refresh token is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh_token_obj = RefreshToken(refresh_token)
            refresh_token_obj.blacklist()

            response = Response(
                {
                    "status": "success",
                    "message": "Successfully logged out",
                },
                status=status.HTTP_204_NO_CONTENT,
            )

            response.delete_cookie("refresh_token", path="/")
            response.delete_cookie("access_token", path="/")

            return response
        except TokenError as e:
            return Response(
                {
                    "status": "error",
                    "message": "Token error occurred",
                    "data": None,
                    "errors": {"token": str(e)},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred",
                    "data": None,
                    "errors": {"exception": str(e)},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response(
                {
                    "status": "error",
                    "message": "Authentication failed.",
                    "data": None,
                    "errors": e.detail,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = serializer.validated_data["user"]
        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]

        response = Response(
            {
                "status": "success",
                "message": "Authentication successful.",
                "data": {"user": user},
                "errors": {},
            },
            status=status.HTTP_200_OK,
        )

        expiry = datetime.utcnow() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        response.set_cookie(
            "access_token",
            access,
            expires=expiry,
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        expiry = datetime.utcnow() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        response.set_cookie(
            "refresh_token",
            refresh,
            expires=expiry,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {
                    "status": "error",
                    "message": "Refresh token is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        mutable_data = QueryDict("", mutable=True)
        mutable_data.update(request.data)
        mutable_data["refresh"] = refresh_token

        request._full_data = mutable_data

        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                access_token = response.data["access"]

                response.set_cookie(
                    "access_token",
                    access_token,
                    expires=now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                    httponly=True,
                    secure=True,
                    samesite="Lax",
                )
                response.data = {
                    "status": "success",
                    "message": "Access token refreshed successfully",
                }
            return response
        except TokenError as e:
            return Response(
                {
                    "status": "error",
                    "message": "Token error occurred",
                    "data": None,
                    "errors": {"token": str(e)},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred",
                    "data": None,
                    "errors": {"exception": str(e)},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Password reset link sent",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Invalid email",
                "data": None,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Password has been reset",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Invalid token or user ID",
                "data": None,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(
            {"status": "success", "message": "Account deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
