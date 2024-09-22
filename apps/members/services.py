from rest_framework import serializers

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
    def create_member_profile(user):
        return MemberProfile.objects.create(user=user)

    @staticmethod
    def initialize_store_notifications(member: MemberProfile):
        MemberNotificationPreferences.objects.create(member=member)
