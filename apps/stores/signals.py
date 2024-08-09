from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model

from apps.accounts.signals import user_activated
from apps.accounts.models import User as UserModel
from apps.stores.models import (
    StoreProfile,
    StoreNotificationPreferences,
)
from apps.emails.services.email_senders import StoreEmailSender
from apps.stores.services.tag_manager import TagHandler
from apps.payments.signals import tags_purchased


User = get_user_model()


@receiver(user_activated, sender=User)
def create_store_profile(sender, instance: UserModel, **kwargs):
    if instance.is_active and instance.role == "store":
        store_profile, created = StoreProfile.objects.get_or_create(user=instance)
        if created:
            StoreNotificationPreferences.objects.create(store=store_profile)


@receiver(post_save, sender=StoreProfile)
def send_pin_email_to_store(sender, instance: StoreProfile, created: bool, **kwargs):
    if created:
        StoreEmailSender(instance).send_welcome_email()


@receiver(pre_save, sender=User)
def track_email_change(sender, instance: StoreProfile, **kwargs):
    if instance.pk:
        old_email = User.objects.get(pk=instance.pk).email
        instance._old_email = old_email


@receiver(post_save, sender=User)
def update_store_notification_preference(sender, instance: StoreProfile, **kwargs):
    if hasattr(instance, "_old_email") and instance.email != instance._old_email:
        store_profile = StoreProfile.objects.filter(user=instance).first()
        if store_profile:
            notification_preferences = store_profile.notification_preferences
            if notification_preferences.secondary_email == instance._old_email:
                notification_preferences.secondary_email = instance.email
                notification_preferences.save()


@receiver(tags_purchased)
def create_tag_group_and_tags(sender, instance: StoreProfile, **kwargs):
    tag_count = kwargs.get('tag_count')
    if not tag_count:
        raise ValueError("tag_count is required")
    
    tag_handler = TagHandler()
    tag_handler.create_tag_group_and_tags(instance, tag_count)
