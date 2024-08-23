from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import update_last_login

from rest_framework import serializers

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from apps.emails.services.email_senders import AccountEmailSender
from apps.accounts.services.signup_services import SignupService, UsernameValidator
from apps.stores.serializers import (
    StoreProfileSerializer,
    StoreAddressSerializer,
    StoreOpeningHoursSerializer,
)

User = get_user_model()


class MemberSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[UsernameValidator()])
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data: dict):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match")

        try:
            validate_password(data["password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data

    def create(self, validated_data):
        validated_data["role"] = "member"

        return SignupService().create_member_user(validated_data)


class StoreSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[UsernameValidator()])
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm Password"
    )
    store = StoreProfileSerializer(required=True)
    address = StoreAddressSerializer(required=True)
    opening_hours = StoreOpeningHoursSerializer(many=True, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "store",
            "address",
            "opening_hours",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data: dict):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match")

        try:
            validate_password(data["password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data

    def create(self, validated_data):
        validated_data["role"] = "store"

        address_data = self.initial_data.pop("address", None)
        opening_hours_data = self.initial_data.pop("opening_hours", [])
        store_profile_data = self.initial_data.pop("store", None)

        return SignupService().create_store_user(
            validated_data, store_profile_data, address_data, opening_hours_data
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: dict):
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        user = User.objects.filter(
            Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)
        ).first()

        if not user:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "No account found with the given email or username."
                    ]
                }
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials"]}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "User account is not activated. Please check your email."
                    ]
                }
            )

        self.user = user

        refresh = self.get_token(self.user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        data["user"] = {"id": user.id, "username": user.username, "role": user.role}

        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs: dict):
        refresh = RefreshToken(attrs["refresh"])

        decoded_refresh_token = refresh.payload
        user_id = decoded_refresh_token["user_id"]
        user = User.objects.get(id=user_id)

        access_token = refresh.access_token
        access_token["role"] = user.role

        data = {
            "access": str(access_token),
            "refresh": str(refresh),
        }

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No user is associated with this email address"
            )
        return value

    def save(self):
        email = self.validated_data["email"]
        user = User.objects.get(email=email)
        AccountEmailSender(user).send_password_reset_email()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data: dict):
        try:
            uid = force_str(urlsafe_base64_decode(data["uid"]))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user ID")

        if not default_token_generator.check_token(self.user, data["token"]):
            raise serializers.ValidationError("Invalid token")

        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError("Passwords do not match")

        if check_password(data["new_password"], self.user.password):
            raise serializers.ValidationError(
                "The new password cannot be the same as the old password."
            )

        try:
            validate_password(data["new_password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        return data

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
