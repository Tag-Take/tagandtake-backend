from rest_framework import serializers
from apps.members.models import MemberProfile, MemberNotificationPreferences
from apps.members.services import MemberService
from apps.common.constants import *
from apps.common.constants import (
    USERNAME,
    USER,
    PROFILE_PHOTO_URL,
    CREATED_AT,
    UPDATED_AT,
)


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


class MemberProfileImageSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField(required=False)

    class Meta:
        fields = [PROFILE_PHOTO]

    def validate(self, attrs: dict):
        request = self.context.get(REQUEST)
        member = request.user.member

        if request.method == "DELETE" and not member.profile_photo_url:
            raise serializers.ValidationError("No profile photo to delete.")

        if request.method == "POST" and not attrs.get(PROFILE_PHOTO):
            raise serializers.ValidationError(
                "No file found for filed profile_photo to upload."
            )

        attrs[MEMBER] = member
        return attrs

    def save(self):
        member = self.validated_data[MEMBER]
        file = self.validated_data.get(PROFILE_PHOTO)

        if file:
            return MemberService.update_member_profile_photo(member, file)
        else:
            return MemberService.delete_member_profile_photo(member)
