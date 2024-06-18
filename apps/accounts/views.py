from datetime import datetime

from django.utils.timezone import now
from django.http import QueryDict
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.serializers import (
    StoreSignUpSerializer,
    MemberSignUpSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)

User = get_user_model()


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()

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
        serializer_class = self.get_serializer_class()
        if not serializer_class:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid signup type",
                    "data": None,
                    "errors": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = serializer_class(data=request.data)
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


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {
                    "status": "error",
                    "message": "Refresh token is required",
                    "data": None,
                    "errors": {},
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
                    "data": None,
                    "errors": {},
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
                    "data": None,
                    "errors": {},
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
                    "data": None,
                    "errors": {},
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
                    "data": None,
                    "errors": {},
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
                    "data": None,
                    "errors": {},
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
