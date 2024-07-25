from rest_framework import serializers
from apps.members.models import MemberProfile, MemberNotificationPreferences


class MemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfile
        fields = [
            "username",
            "profile_photo_url",
            "member_bio",
            "instagram_url",
            "longitude",
            "latitude"
        ]
        read_only_fields = ["username", "user", "profile_photo_url", "created_at", "updated_at"]

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