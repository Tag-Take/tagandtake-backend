from rest_framework import serializers
from apps.members.models import MemberProfile


class MemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfile
        fields = [
            "username",
            "member_bio",
            "instagram_url",
            "longitude",
            "latitude"
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance