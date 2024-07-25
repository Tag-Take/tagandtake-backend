from django.contrib.auth import authenticate, get_user_model
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

from apps.common.utils.email import send_email
from apps.accounts.utils import (
    generate_password_reset_email_context,
    generate_activation_context,
)


User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(
        write_only=True, required=True, label="Confirm Password"
    )
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2", "role")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        role = validated_data.pop("role")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
        )
        self.send_activation_email(user)
        return user

    @staticmethod
    def send_activation_email(user):
        context = generate_activation_context(user)

        send_email(
            subject="Activate your account",
            to=user.email,
            template_name="./activation_email.html",
            context=context,
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username_or_email = attrs.get("username")
        password = attrs.get("password")

        user = User.objects.filter(username=username_or_email).first()
        user = User.objects.get(
            Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)
        )
        # TODO - Make email verification work ^
        if not user:
            self.username_field = User.EMAIL_FIELD
            user = User.objects.filter(email=username_or_email).first()

        if user and user.check_password(password):
            if not user.is_active:
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "User account is not activated. Please check your email."
                        ]
                    }
                )
        else:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials"]}
            )

        self.user = user
        data = super().validate(attrs)
        data["user"] = {"id": user.id, "username": user.username, "role": user.role}

        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
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

    def validate_email(self, value):
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

        context = generate_password_reset_email_context(user)

        send_email(
            subject="Password Reset Request",
            to=email,
            template_name="./password_reset_email.html",
            context=context,
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
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

        return data

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
