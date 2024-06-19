from rest_framework import serializers
from apps.members.models import MemberProfile

class MemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfile
        fields = "__all__"
