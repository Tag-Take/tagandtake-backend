from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.http import QueryDict
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.serializers import (
    SignUpSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenRefreshSerializer,
)
from apps.accounts.signals import user_activated
from apps.emails.services.email_senders import AccountEmailSender
from apps.common.utils.responses import (
    create_success_response,
    create_error_response,
    JWTCookieHandler,
)


User = get_user_model()

# TODO: Seperate out member and store signup and activation
"""
Requirements (^): 
    - member signup requires adding username, email, password, store nanme, 
      website (optional), address and payment details in one transaction
    - member signup can continue as previously handled. 
"""



class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request: Request, *args, **kwargs):
        signup_type = request.query_params.get("type")
        request.data["role"] = request.query_params.get("type")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return create_success_response(
                f"{signup_type.capitalize()} user created successfully.",
                {"user": serializer.data},
                status.HTTP_201_CREATED,
            )
        else:
            return create_error_response(
                "User creation failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
            )


class ActivateUserView(APIView):
    authentication_classes = []

    def get(self, request: Request, uidb64: str, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save()
                user_activated.send(sender=user.__class__, instance=user)

                response = create_success_response(
                    "Account activated successfully", {}, status.HTTP_200_OK
                )
                access_token, refresh_token = JWTCookieHandler(
                    response
                )._generate_tokens(user)
                return JWTCookieHandler(response).set_jwt_cookies(
                    access_token, refresh_token
                )

            return create_error_response(
                "Account is already active", {}, status.HTTP_400_BAD_REQUEST
            )

        else:
            return create_error_response(
                "Activation link is invalid", {}, status.HTTP_400_BAD_REQUEST
            )


class ResendActivationEmailView(APIView):
    def post(self, request: Request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
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
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return create_error_response(
                "Refresh token is required", {}, status.HTTP_400_BAD_REQUEST
            )

        try:
            response = create_success_response(
                "Successfully logged out", {}, status.HTTP_204_NO_CONTENT
            )
            return JWTCookieHandler(response).delete_jwt_cookies(refresh_token)

        except TokenError as e:
            return create_error_response(
                "Token error occurred", {"token": str(e)}, status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return create_error_response(
                "An error occurred", {"exception": str(e)}, status.HTTP_400_BAD_REQUEST
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return create_error_response(
                "Authentication failed.", e.detail, status.HTTP_401_UNAUTHORIZED
            )

        user = serializer.validated_data["user"]
        access = serializer.validated_data["access"]
        refresh = serializer.validated_data["refresh"]

        response = create_success_response(
            "Authentication successful.", {"user": user}, status.HTTP_200_OK
        )

        return JWTCookieHandler(response).set_jwt_cookies(access, refresh)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request: Request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return create_error_response(
                "Refresh token is required", {}, status.HTTP_400_BAD_REQUEST
            )

        mutable_data = QueryDict("", mutable=True)
        mutable_data.update(request.data)
        mutable_data["refresh"] = refresh_token

        request._full_data = mutable_data

        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                access_token = response.data["access"]

                response = create_success_response(
                    "Access token refreshed successfully", {}, status.HTTP_200_OK
                )
                return JWTCookieHandler(response).set_jwt_cookies(access_token)

        except TokenError as e:
            return create_error_response(
                "Token error occurred", {"token": str(e)}, status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return create_error_response(
                "An error occurred", {"exception": str(e)}, status.HTTP_400_BAD_REQUEST
            )


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            response = create_success_response(
                "Password has been reset and user has been logged out from all sessions.",
                {},
                status.HTTP_200_OK,
            )
            return JWTCookieHandler(response).delete_jwt_cookies()

        return create_error_response(
            "Invalid email", serializer.errors, status.HTTP_400_BAD_REQUEST
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            refresh_token = request.COOKIES.get("refresh_token")

            response = create_success_response(
                "Password has been reset and user has been logged out from all sessions.",
                {},
                status.HTTP_200_OK,
            )
            return JWTCookieHandler(response).delete_jwt_cookies(refresh_token)

        return create_error_response(
            "Error setting new password", serializer.errors, status.HTTP_400_BAD_REQUEST
        )


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, *args, **kwargs):
        user = request.user
        user.delete()
        return create_success_response(
            "Account deleted successfully", {}, status.HTTP_204_NO_CONTENT
        )
