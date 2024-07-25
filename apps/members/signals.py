from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model

from apps.accounts.signals import user_activated
from apps.members.models import (
    MemberProfile, MemberNotificationPreferences
)
from apps.members.utils import send_welcome_email


User = get_user_model()


@receiver(user_activated, sender=User)
def create_member_profile(sender, instance, **kwargs):
    if instance.is_active and instance.role == "member":
        member_profile, created = MemberProfile.objects.get_or_create(user=instance)
        if created:
            MemberNotificationPreferences.objects.create(member=member_profile)


@receiver(post_save, sender=MemberProfile)
def send_member_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_welcome_email(instance)


@receiver(pre_save, sender=User)
def track_email_change(sender, instance, **kwargs):
    if instance.pk:
        old_email = User.objects.get(pk=instance.pk).email
        instance._old_email = old_email


@receiver(post_save, sender=User)
def update_store_notification_preference(sender, instance, **kwargs):
    if hasattr(instance, "_old_email") and instance.email != instance._old_email:
        member_profile = MemberProfile.objects.filter(user=instance).first()
        if member_profile:
            notification_preferences = member_profile.notification_preferences
            if notification_preferences.secondary_email == instance._old_email:
                notification_preferences.secondary_email = instance.email
                notification_preferences.save()
