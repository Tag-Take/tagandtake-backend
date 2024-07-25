from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.http import QueryDict
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.timezone import now

from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.serializers import (
    SignUpSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenRefreshSerializer,
)
from apps.accounts.utils import generate_activation_context
from apps.accounts.signals import user_activated
from apps.common.utils.email import send_email
from apps.common.utils.responses import create_success_response, create_error_response


User = get_user_model()


class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        signup_type = request.query_params.get("type")
        request.data["role"] = request.query_params.get("type")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return create_success_response(
                f"{signup_type.capitalize()} user created successfully.",
                {"user": serializer.data},
                status.HTTP_201_CREATED
            )
        else:
            return create_error_response(
                "User creation failed.",
                serializer.errors,
                status.HTTP_400_BAD_REQUEST
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

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Set the tokens in cookies
            expiry = datetime.utcnow() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
            response = create_success_response("Account activated successfully", {}, status.HTTP_200_OK)
            response.set_cookie(
                "access_token",
                access_token,
                expires=expiry,
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SAME_SITE_COOKIE,
                domain=settings.DOMAIN,
            )
            expiry = datetime.utcnow() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
            response.set_cookie(
                "refresh_token",
                refresh_token,
                expires=expiry,
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SAME_SITE_COOKIE,
                domain=settings.DOMAIN,
            )

            return response
        else:
            return create_error_response("Activation link is invalid", {}, status.HTTP_400_BAD_REQUEST)

class ResendActivationEmailView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return create_error_response("User is already active.", {}, status.HTTP_400_BAD_REQUEST)
            else:
                context = generate_activation_context(user)
                send_email(
                    subject="Activate your account",
                    to=user.email,
                    template_name="./activation_email.html",
                    context=context,
                )
                return create_success_response("Activation email sent.", {}, status.HTTP_200_OK)
        except User.DoesNotExist:
            return create_error_response("No user associated with this email.", {}, status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return create_error_response("Refresh token is required", {}, status.HTTP_400_BAD_REQUEST)

        try:
            refresh_token_obj = RefreshToken(refresh_token)
            refresh_token_obj.blacklist()

            response = create_success_response("Successfully logged out", {}, status.HTTP_204_NO_CONTENT)
            response.delete_cookie("refresh_token", path="/")
            response.delete_cookie("access_token", path="/")

            return response
        except TokenError as e:
            return create_error_response("Token error occurred", {"token": str(e)}, status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return create_error_response("An error occurred", {"exception": str(e)}, status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return create_error_response("Authentication failed.", e.detail, status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data["user"]
        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]

        response = create_success_response("Authentication successful.", {"user": user}, status.HTTP_200_OK)

        expiry = datetime.utcnow() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        response.set_cookie(
            "access_token",
            access,
            expires=expiry,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SAME_SITE_COOKIE,
            domain=settings.DOMAIN,
        )
        expiry = datetime.utcnow() + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
        response.set_cookie(
            "refresh_token",
            refresh,
            expires=expiry,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SAME_SITE_COOKIE,
            domain=settings.DOMAIN,
        )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return create_error_response("Refresh token is required", {}, status.HTTP_400_BAD_REQUEST)

        mutable_data = QueryDict("", mutable=True)
        mutable_data.update(request.data)
        mutable_data["refresh"] = refresh_token

        request._full_data = mutable_data

        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                access_token = response.data["access"]

                response = create_success_response("Access token refreshed successfully", {}, status.HTTP_200_OK)

                response.set_cookie(
                    "access_token",
                    access_token,
                    expires=now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                    httponly=True,
                    secure=settings.SESSION_COOKIE_SECURE,
                    samesite=settings.SAME_SITE_COOKIE,
                    domain=settings.DOMAIN,
                )
            return response
        except TokenError as e:
            return create_error_response("Token error occurred", {"token": str(e)}, status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return create_error_response("An error occurred", {"exception": str(e)}, status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            response = create_success_response(
                "Password has been reset and user has been logged out from all sessions.",
                {},
                status.HTTP_200_OK,
            )
            response.delete_cookie("refresh_token")
            response.delete_cookie("access_token")

            return response
        return create_error_response("Invalid email", serializer.errors, status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                try:
                    refresh_token_obj = RefreshToken(refresh_token)
                    refresh_token_obj.blacklist()
                except TokenError:
                    pass

            response = create_success_response(
                "Password has been reset and user has been logged out from all sessions.",
                {},
                status.HTTP_200_OK,
            )
            response.delete_cookie("refresh_token", path="/")
            response.delete_cookie("access_token", path="/")

            return response

        return create_error_response("Error setting new password", serializer.errors, status.HTTP_400_BAD_REQUEST)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return create_success_response("Account deleted successfully", {}, status.HTTP_204_NO_CONTENT)