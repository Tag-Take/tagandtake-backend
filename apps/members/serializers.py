from rest_framework import serializers
from apps.members.models import MemberProfile, MemberNotificationPreferences
from apps.common.s3.s3_utils import S3ImageHandler
from apps.common.s3.s3_config import (
    get_member_profile_photo_key,
    FILE_NAMES,
    IMAGE_FILE_TYPE,
)
from apps.common.constants import *


class MemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfile
        fields = [
            USERNAME,
            PROFILE_PHOTO_URL,
            MEMBER_BIO,
            INSTAGRAM_URL,
            LONGITUDE,
            LATITUDE,
        ]
        read_only_fields = [
            USERNAME,
            USER,
            PROFILE_PHOTO_URL,
            CREATED_AT,
            UPDATED_AT,
        ]

    def update(self, member: MemberProfile, validated_data: dict):
        for attr, value in validated_data.items():
            setattr(member, attr, value)
        member.save()
        return member


class MemberNotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberNotificationPreferences
        fields = [
            SECONDARY_EMAIL,
            MOBILE,
            EMAIL_NOTIFICATIONS,
            MOBILE_NOTIFICATIONS,
        ]
        read_only_fields = [USER]

    def update(
        self, member_notifications: MemberNotificationPreferences, validated_data: dict
    ):
        for attr, value in validated_data.items():
            setattr(member_notifications, attr, value)
        member_notifications.save()
        return member_notifications


class MemberProfileImageUploadSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()

    def validate(self, attrs: dict):
        request = self.context.get(REQUEST)
        try:
            profile = MemberProfile.objects.get(user=request.user)
        except MemberProfile.DoesNotExist:
            raise serializers.ValidationError("Store profile not found.")

        attrs[PROFILE] = profile
        return attrs

    def save(self):
        memeber: MemberProfile = self.validated_data[PROFILE]
        file = self.validated_data[PROFILE_PHOTO]

        s3_handler = S3ImageHandler()
        key = get_member_profile_photo_key(memeber)

        try:
            image_url = s3_handler.upload_image(file, key)
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to upload profile photo: {str(e)}"
            )

        memeber.profile_photo_url = image_url
        memeber.save()
        return memeber


class MemberProfileImageDeleteSerializer(serializers.Serializer):
    def validate(self, attrs: dict):
        request = self.context.get(REQUEST)
        try:
            profile = MemberProfile.objects.get(user=request.user)
        except MemberProfile.DoesNotExist:
            raise serializers.ValidationError("Store profile not found.")

        if not profile.profile_photo_url:
            raise serializers.ValidationError("No profile photo to delete.")

        attrs[PROFILE] = profile
        return attrs

    def save(self):
        member: MemberProfile = self.validated_data[PROFILE]
        key = get_member_profile_photo_key(member)

        s3_handler = S3ImageHandler()
        try:
            s3_handler.delete_image(key)
            member.profile_photo_url = None
            member.save()
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to delete profile photo: {str(e)}"
            )
        return member
