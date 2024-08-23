from rest_framework import serializers
from apps.members.models import MemberProfile, MemberNotificationPreferences
from apps.common.s3.s3_utils import S3ImageHandler
from apps.common.s3.s3_config import (
    get_member_profile_folder,
    FILE_NAMES,
    IMAGE_FILE_TYPE,
)


class MemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfile
        fields = [
            "username",
            "profile_photo_url",
            "member_bio",
            "instagram_url",
            "longitude",
            "latitude",
        ]
        read_only_fields = [
            "username",
            "user",
            "profile_photo_url",
            "created_at",
            "updated_at",
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
            "secondary_email",
            "mobile",
            "email_notifications",
            "mobile_notifications",
        ]
        read_only_fields = ["user"]

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
        request = self.context.get("request")
        try:
            profile = MemberProfile.objects.get(user=request.user)
        except MemberProfile.DoesNotExist:
            raise serializers.ValidationError("Store profile not found.")

        attrs["profile"] = profile
        return attrs

    def save(self):
        memeber: MemberProfile = self.validated_data["profile"]
        file = self.validated_data["profile_photo"]

        s3_handler = S3ImageHandler()
        folder_name = get_member_profile_folder(memeber.id)
        key = f"{folder_name}/{FILE_NAMES['profile_photo']}.{IMAGE_FILE_TYPE}"

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
        request = self.context.get("request")
        try:
            profile = MemberProfile.objects.get(user=request.user)
        except MemberProfile.DoesNotExist:
            raise serializers.ValidationError("Store profile not found.")

        if not profile.profile_photo_url:
            raise serializers.ValidationError("No profile photo to delete.")

        attrs["profile"] = profile
        return attrs

    def save(self):
        member: MemberProfile = self.validated_data["profile"]
        folder_name = get_member_profile_folder(member.id)
        key = f"{folder_name}/{FILE_NAMES['profile_photo']}.{IMAGE_FILE_TYPE}"

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
