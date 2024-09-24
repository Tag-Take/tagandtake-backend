from rest_framework import serializers
from apps.members.models import MemberProfile, MemberNotificationPreferences
from members.services import MemberService
from apps.common.s3.s3_utils import S3Service
from apps.common.s3.s3_config import get_member_profile_photo_key
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
        member = MemberService.update_member_profile(member, validated_data)


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
        member_notifications = MemberService.update_member_notifications(
            member_notifications, validated_data
        )
        return member_notifications

class MemberProfileImageUploadSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()

    def validate(self, attrs: dict):
        request = self.context.get(REQUEST)
        attrs[PROFILE] = MemberService.get_member_by_user(request.user)
        return attrs

    def save(self):
        memeber: MemberProfile = self.validated_data[PROFILE]
        file = self.validated_data[PROFILE_PHOTO]
        member = MemberService.update_member_profile_photo(memeber, file) 
        return member


class MemberProfileImageDeleteSerializer(serializers.Serializer):
    def validate(self, attrs: dict):
        request = self.context.get(REQUEST)
        member = MemberService.get_member_by_user(request.user)
        if not member.profile_photo_url:
            raise serializers.ValidationError("No profile photo to delete.")
        attrs[PROFILE] = member
        return attrs

    def save(self):
        member: MemberProfile = self.validated_data[PROFILE]
        member = MemberService.delete_member_profile_photo(member)
        return member
