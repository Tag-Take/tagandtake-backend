from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model

from apps.accounts.signals import user_activated
from apps.stores.models import StoreProfile, StoreNotificationPreferences, TagGroup, Tag

from apps.stores.utils import send_pin_email

User = get_user_model()


@receiver(user_activated, sender=User)
def create_store_profile(sender, instance, **kwargs):
    if instance.is_active and instance.role == "store":
        store_profile, created = StoreProfile.objects.get_or_create(user=instance)
        if created:
            StoreNotificationPreferences.objects.create(store=store_profile)


@receiver(post_save, sender=StoreProfile)
def send_pin_email_to_store(sender, instance, created, **kwargs):
    if created:
        send_pin_email(instance)


@receiver(pre_save, sender=User)
def track_email_change(sender, instance, **kwargs):
    if instance.pk:
        old_email = User.objects.get(pk=instance.pk).email
        instance._old_email = old_email


@receiver(post_save, sender=User)
def update_store_notification_preference(sender, instance, **kwargs):
    if hasattr(instance, "_old_email") and instance.email != instance._old_email:
        store_profile = StoreProfile.objects.filter(user=instance).first()
        if store_profile:
            notification_preferences = store_profile.notification_preferences
            if notification_preferences.secondary_email == instance._old_email:
                notification_preferences.secondary_email = instance.email
                notification_preferences.save()


@receiver(post_save, sender=TagGroup)
def activate_tag_group(sender, instance, created, **kwargs):
    if instance.activated and not instance.activated_at:
        instance.activated_at = instance.created_at
        instance.save()
        Tag.objects.filter(tag_group=instance).update(status="active")
