from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model

from apps.accounts.signals import user_activated
from apps.accounts.models import User as UserModel
from apps.members.models import MemberProfile, MemberNotificationPreferences
from apps.emails.services.email_senders import MemberEmailSender


User = get_user_model()


@receiver(user_activated, sender=User)
def seend_wemcome_email(sender: Signal, instance: UserModel, **kwargs):
    if instance.is_active and instance.role == "member":
        memeber: MemberProfile = MemberProfile.objects.get(user=instance)
        MemberEmailSender(memeber).send_welcome_email()


@receiver(pre_save, sender=User)
def track_email_change(sender, instance: UserModel, **kwargs):
    if instance.pk:
        old_email = User.objects.get(pk=instance.pk).email
        instance._old_email = old_email


@receiver(post_save, sender=User)
def update_store_notification_preference(sender, instance: UserModel, **kwargs):
    if hasattr(instance, "_old_email") and instance.email != instance._old_email:
        member: MemberProfile = MemberProfile.objects.filter(user=instance).first()
        if member:
            notification_preferences: MemberNotificationPreferences = (
                member.notification_preferences
            )
            if notification_preferences.secondary_email == instance._old_email:
                notification_preferences.secondary_email = instance.email
                notification_preferences.save()
