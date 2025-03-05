from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from apps.common.constants import *
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
from apps.stores.permissions import IsStoreWithValidPIN
from apps.members.permissions import IsMemberUser

User = get_user_model()


class MemberSignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = MemberSignUpSerializer
    throttle_scope = SIGNUP


class StoreSignUpView(generics.CreateAPIView):
    serializer_class = StoreSignUpSerializer
    throttle_scope = SIGNUP

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        return serializer.save()


class ActivateUserView(APIView):
    authentication_classes = []

    def get(self, request, uidb64, token):
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
                access_token, refresh_token = JWTManager.generate_tokens(user)
                response = Response(
                    {
                        "message": "Account activated successfully",
                        ROLE: user.role,
                    },
                    status=status.HTTP_200_OK,
                )
                return response

            return Response(
                {"error": "Account is already active"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"error": "Activation link is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResendActivationEmailView(APIView):
    throttle_scope = "resend_activation"

    def post(self, request):
        email = request.data.get(EMAIL)
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {"error": "User is already active."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                AccountEmailSender(user).send_activation_email()
                return Response(
                    {"message": "Activation email sent."}, status=status.HTTP_200_OK
                )
        except User.DoesNotExist:
            return Response(
                {"error": "No user associated with this email."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(REFRESH)
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            JWTManager.blacklist_refresh_token(refresh_token)
            response = Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_204_NO_CONTENT,
            )
            return JWTManager.clear_refresh_token_cookie(response)
        except TokenError as e:
            return Response(
                {"error": f"Token error occurred: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["GET"])
def get_auth_status(request):
    user = request.user
    if user.is_authenticated:
        return Response(
            {
                "message": "User is authenticated",
                ROLE: user.role,
            },
            status=status.HTTP_200_OK,
        )
    return Response(
        {"message": "User is not authenticated", ISLOGGEDIN: False, ROLE: None},
        status=status.HTTP_200_OK,
    )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_scope = LOGIN

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            return JWTManager.set_refresh_token_cookie(
                response, response.data["refresh"]
            )
        return response


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            response = JWTManager.set_refresh_token_cookie(
                response, response.data[REFRESH]
            )
            del response.data[REFRESH]
            return response

        return response


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    throttle_scope = PASSWORD_RESET

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password reset email has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    throttle_scope = PASSWORD_RESET

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        if user.role == STORE:
            pin = request.data.get(PIN)
            if not pin:
                return Response(
                    {"error": "PIN is required."}, status=status.HTTP_400_BAD_REQUEST
                )
            try:
                profile = Store.objects.get(user=user)
            except Store.DoesNotExist:
                return Response(
                    {"error": "Store profile not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not profile.validate_pin(pin):
                return Response(
                    {"error": "Invalid PIN."}, status=status.HTTP_400_BAD_REQUEST
                )
        user.delete()
        return Response(
            {"message": "Account deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class MemberDeleteAccountView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsMemberUser]

    def get_object(self):
        return self.request.user


class StoreDeleteAccountView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsStoreWithValidPIN]

    def get_object(self):
        return self.request.user
