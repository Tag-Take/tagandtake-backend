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

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MemberProfileImageUploadSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()

    def validate(self, attrs):
        request = self.context.get("request")
        try:
            profile = MemberProfile.objects.get(user=request.user)
        except MemberProfile.DoesNotExist:
            raise serializers.ValidationError("Store profile not found.")

        attrs["profile"] = profile
        return attrs

    def save(self):
        profile = self.validated_data["profile"]
        file = self.validated_data["profile_photo"]

        s3_handler = S3ImageHandler()
        folder_name = get_member_profile_folder(profile.id)
        key = f"{folder_name}/{FILE_NAMES['profile_photo']}.{IMAGE_FILE_TYPE}"

        try:
            image_url = s3_handler.upload_image(file, key)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to upload profile photo: {str(e)}")

        profile.profile_photo_url = image_url
        profile.save()
        return profile


class MemberProfileImageDeleteSerializer(serializers.Serializer):
    def validate(self, attrs):
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
        profile = self.validated_data["profile"]
        folder_name = get_member_profile_folder(profile.id)
        key = f"{folder_name}/{FILE_NAMES['profile_photo']}.{IMAGE_FILE_TYPE}"

        s3_handler = S3ImageHandler()
        try:
            s3_handler.delete_image(key)
            profile.profile_photo_url = None
            profile.save()
        except Exception as e:
            raise serializers.ValidationError(f"Failed to delete profile photo: {str(e)}")
        return profile
