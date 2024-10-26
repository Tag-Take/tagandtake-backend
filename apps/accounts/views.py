from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.http import QueryDict
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework.throttling import ScopedRateThrottle

from rest_framework.decorators import api_view
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.common.constants import *
from apps.accounts.models import User as UserModel
from apps.accounts.serializers import (
    MemberSignUpSerializer,
    StoreSignUpSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    CookieTokenRefreshSerializer,
)
from apps.accounts.jwt_manager import JWTManager
from apps.stores.models import StoreProfile as Store
from apps.accounts.signals import user_activated
from apps.notifications.emails.services.email_senders import AccountEmailSender
from apps.common.responses import (
    create_success_response,
    create_error_response,
)


User = get_user_model()


class MemberSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = MemberSignUpSerializer
    throttle_scope = SIGNUP

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user: UserModel = serializer.save()
                return create_success_response(
                    "Member created successfully.",
                    {USER: user.username},
                    status.HTTP_201_CREATED,
                )
            except serializers.ValidationError as e:
                return create_error_response(
                    "User creation failed.", e.detail, status.HTTP_400_BAD_REQUEST
                )
        else:
            return create_error_response(
                "User creation failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
            )


class StoreSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StoreSignUpSerializer
    throttle_scope = SIGNUP

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user: UserModel = serializer.save()
                return create_success_response(
                    "Store created successfully.",
                    {USER: user.username},
                    status.HTTP_201_CREATED,
                )
            except serializers.ValidationError as e:
                return create_error_response(
                    "User creation failed.", e.detail, status.HTTP_400_BAD_REQUEST
                )
        else:
            return create_error_response(
                "User creation failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
            )


class ActivateUserView(APIView):
    authentication_classes = []
    throttle_scope = RESEND_ACTIVATION

    def get(self, request: Request, uidb64: str, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user: UserModel = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save()
                user_activated.send(sender=user.__class__, instance=user)
                access_token, refresh_token = JWTManager.generate_tokens(user)
                response = create_success_response(
                    "Account activated successfully",
                    {
                        ACCESS_TOKEN: access_token,
                        ROLE: user.role,
                        ISLOGGEDIN: True,
                    },
                    status.HTTP_200_OK,
                )
                return JWTManager(response).set_refresh_token_cookie(refresh_token)

            return create_error_response(
                "Account is already active", {}, status.HTTP_400_BAD_REQUEST
            )

        else:
            return create_error_response(
                "Activation link is invalid", {}, status.HTTP_400_BAD_REQUEST
            )


class ResendActivationEmailView(APIView):
    throttle_scope = "resend_activation"

    def post(self, request: Request, *args, **kwargs):
        email = request.data.get(EMAIL)
        try:
            user: UserModel = User.objects.get(email=email)
            if user.is_active:
                return create_error_response(
                    "User is already active.", {}, status.HTTP_400_BAD_REQUEST
                )
            else:
                AccountEmailSender(user).send_activation_email()
                return create_success_response(
                    "Activation email sent.", {}, status.HTTP_200_OK
                )
        except User.DoesNotExist:
            return create_error_response(
                "No user associated with this email.", {}, status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    def post(self, request: Request, *args, **kwargs):
        refresh_token = request.COOKIES.get(REFRESH_TOKEN)
        if not refresh_token:
            return create_error_response(
                "Refresh token is required", {}, status.HTTP_400_BAD_REQUEST
            )

        try:
            response = create_success_response(
                "Successfully logged out", {}, status.HTTP_204_NO_CONTENT
            )
            JWTManager.blacklist_refresh_token(refresh_token)
            return JWTManager.clear_refresh_token_cookie(response)

        except TokenError as e:
            return create_error_response(
                "Token error occurred", {TOKEN: str(e)}, status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return create_error_response(
                "An error occurred", {"exception": str(e)}, status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET"])
def get_auth_status(request: Request):
    user = request.user
    if user.is_authenticated:
        return create_success_response(
            "User is authenticated",
            {USER: user.username, ISLOGGEDIN: True, ROLE: user.role},
            status.HTTP_200_OK,
        )
    return create_success_response(
        "User is not authenticated", {ISLOGGEDIN: False, ROLE: None}, status.HTTP_200_OK
    )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = LOGIN

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return create_error_response(
                "Authentication failed.", e.detail, status.HTTP_401_UNAUTHORIZED
            )

        user: UserModel = serializer.validated_data[USER]
        access_token = serializer.validated_data[ACCESS]
        refresh_token = serializer.validated_data[REFRESH]

        response = create_success_response(
            "Authentication successful.",
            {
                USERNAME: user.username,
                ACCESS_TOKEN: access_token,
                ISLOGGEDIN: True,
                ROLE: user.role,
            },
            status.HTTP_200_OK,
        )

        return JWTManager.set_refresh_token_cookie(response, refresh_token)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(REFRESH_TOKEN)

        if not refresh_token:
            return create_error_response(
                "Refresh token is missing from cookies", {}, status.HTTP_400_BAD_REQUEST
            )

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            new_refresh_token = response.data.get(REFRESH)
            new_access_token = response.data.get(ACCESS)

            response = create_success_response(
                "Token refreshed successfully",
                {ACCESS_TOKEN: new_access_token},
                status.HTTP_200_OK,
            )

        return JWTManager.set_refresh_token_cookie(response, new_refresh_token)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    throttle_scope = PASSWORD_RESET

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return create_success_response(
                "Password has been reset and user has been logged out from all sessions.",
                {},
                status.HTTP_200_OK,
            )

        return create_error_response(
            "Invalid email", serializer.errors, status.HTTP_400_BAD_REQUEST
        )


# TODO:handle auth on reset
#
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    throttle_scope = PASSWORD_RESET

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            refresh_token = request.COOKIES.get(REFRESH_TOKEN)

            return create_success_response(
                "Password has been reset and user has been logged out from all sessions.",
                {},
                status.HTTP_200_OK,
            )

        return create_error_response(
            "Error setting new password", serializer.errors, status.HTTP_400_BAD_REQUEST
        )


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, *args, **kwargs):
        user = request.user
        if user.role == STORE:
            pin = request.data.get(PIN)
            if not pin:
                return create_error_response(
                    "PIN is required.",
                    {PIN: ["PIN is required"]},
                    status.HTTP_400_BAD_REQUEST,
                )
            profile = Store.objects.get(user=user)
            if not profile:
                return create_error_response(
                    "Store profile not found.", {}, status.HTTP_400_BAD_REQUEST
                )
            if not profile.validate_pin(pin):
                return create_error_response(
                    "Invalid PIN.",
                    {PIN: ["Invalid PIN"]},
                    status.HTTP_400_BAD_REQUEST,
                )
        user.delete()
        return create_success_response(
            "Account deleted successfully", {}, status.HTTP_204_NO_CONTENT
        )
