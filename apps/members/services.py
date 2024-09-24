from rest_framework import serializers

from apps.common.s3.s3_utils import S3Service
from apps.common.s3.s3_config import get_member_profile_photo_key
from apps.members.models import MemberProfile
from apps.members.models import MemberNotificationPreferences


class MemberService:
    @staticmethod
    def get_member(member_id: int):
        try:
            return MemberProfile.objects.get(id=member_id)
        except MemberProfile.DoesNotExist:
            raise serializers.ValidationError("Member does not exist.")

    @staticmethod
    def get_member_by_user(user):
        try:
            return MemberProfile.objects.get(user=user)
        except MemberProfile.DoesNotExist:
            raise serializers.ValidationError("Member does not exist.")

    @staticmethod
    def create_member_profile(user):
        try:
            return MemberProfile.objects.create(user=user)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create member profile: {e}")

    @staticmethod
    def initialize_store_notifications(member: MemberProfile):
        try: 
            MemberNotificationPreferences.objects.create(member=member)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create member notifications: {e}")

    @staticmethod
    def update_member_profile(member: MemberProfile, validated_data: dict):
        try: 
            for key, value in validated_data.items():
                setattr(member, key, value)
            member.save()
            return member
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update member profile: {e}")

    @staticmethod
    def update_member_notifications(
            member_notifications: MemberNotificationPreferences, 
            validated_data: dict
        ):
        try: 
            for attr, value in validated_data.items():
                setattr(member_notifications, attr, value)
            member_notifications.save()
            return member_notifications
        except Exception as e:
            raise serializers.ValidationError(f"Failed to update member notifications: {e}")
    
    @staticmethod
    def update_member_profile_photo(member: MemberProfile, file):
        image_url = MemberService.upload_profile_photo_to_s3(member, file)
        member = MemberService.save_profile_photo_url(member, image_url)
        return member

    @staticmethod
    def save_profile_photo_url(member: MemberProfile, image_url: str):
        try:
            member.profile_photo_url = image_url
            member.save()
            return member
        except Exception as e:
            raise serializers.ValidationError(f"Failed to save profile photo url: {e}")
    
    @staticmethod
    def upload_profile_photo_to_s3(member: MemberProfile, file):
        try:
            key = get_member_profile_photo_key(member)
            image_url = S3Service().upload_image(file, key)
            return image_url
        except Exception as e:
            raise serializers.ValidationError(f"Failed to upload profile photo to s3: {e}")
    
    @staticmethod
    def delete_member_profile_photo(member: MemberProfile):
        MemberService.delete_profile_photo_in_s3(member)
        member = MemberService.delete_profile_photo_url(member)
        return member
    
    @staticmethod
    def delete_profile_photo_in_s3(member: MemberProfile):
        try:
            key = get_member_profile_photo_key(member)
            S3Service().delete_image(key)
        except Exception as e:
            raise serializers.ValidationError(f"Failed to delete profile photo in s3: {e}")

    @staticmethod
    def delete_profile_photo_url(member: MemberProfile):
        try:
            member.profile_photo_url = None
            member.save()
            return member
        except Exception as e:
            raise serializers.ValidationError(f"Failed to delete profile photo url: {e}")
