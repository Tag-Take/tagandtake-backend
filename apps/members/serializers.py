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


class MemberProfileImageSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(write_only=True, required=False)
    profile_photo_url = serializers.URLField(read_only=True)

    class Meta:
        model = MemberProfile
        fields = [PROFILE_PHOTO, PROFILE_PHOTO_URL]

    def update(self, instance, validated_data):
        profile_photo = validated_data.get(PROFILE_PHOTO)
        if profile_photo:
            instance = MemberService.update_member_profile_photo(instance, profile_photo)
        elif self.context['request'].method == 'DELETE':
            instance = MemberService.delete_member_profile_photo(instance)
        return instance
    

class MemberProfileImageSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(write_only=True)
    profile_photo_url = serializers.URLField(read_only=True)

    class Meta:
        model = MemberProfile
        fields = [PROFILE_PHOTO, PROFILE_PHOTO_URL]
        read_only_fields = [PROFILE_PHOTO_URL]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context['request'].method == 'POST':
            self.fields[PROFILE_PHOTO].required = True
        else:
            self.fields[PROFILE_PHOTO].required = False

    def update(self, instance, validated_data):
        profile_photo = validated_data.get(PROFILE_PHOTO)
        if profile_photo:
            instance = MemberService.update_member_profile_photo(instance, profile_photo)
        elif self.context['request'].method == 'DELETE':
            instance = MemberService.delete_member_profile_photo(instance)
        return instance
