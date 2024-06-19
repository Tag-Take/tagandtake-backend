from django.dispatch import receiver

from apps.accounts.signals import user_activated
from apps.members.models import MemberProfile, MemberNotificationPreferences
from apps.accounts.models import User


@receiver(user_activated, sender=User)
def create_member_profile(sender, instance, **kwargs):
    if instance.is_active and instance.role == "member":
        member_profile, created = MemberProfile.objects.get_or_create(user=instance)
        if created:
            MemberNotificationPreferences.objects.create(member=member_profile)
