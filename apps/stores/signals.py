from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model

from apps.accounts.signals import user_activated
from apps.accounts.models import User as UserModel
from apps.stores.models import (
    StoreProfile,
)
from apps.notifications.emails.services.email_senders import StoreEmailSender
from apps.stores.handlers import CreateTagsHandler
from apps.payments.signals import tags_purchased
from apps.accounts.models import User
from apps.common.constants import TAG_COUNT


User = get_user_model()


@receiver(user_activated, sender=User)
def seend_wemcome_email(sender, instance: UserModel, **kwargs):
    if instance.is_active and instance.role == User.Roles.STORE:
        store_profile = StoreProfile.objects.get(user=instance)
        if store_profile:
            StoreEmailSender(store_profile).send_welcome_email()


@receiver(pre_save, sender=User)
def track_email_change(sender, instance: UserModel, **kwargs):
    if instance.pk:
        old_email = User.objects.get(pk=instance.pk).email
        instance._old_email = old_email


@receiver(post_save, sender=User)
def update_store_notification_preference(sender, instance: UserModel, **kwargs):
    if hasattr(instance, "_old_email") and instance.email != instance._old_email:
        store_profile = StoreProfile.objects.filter(user=instance).first()
        if store_profile:
            notification_preferences = store_profile.notification_preferences
            if notification_preferences.secondary_email == instance._old_email:
                notification_preferences.secondary_email = instance.email
                notification_preferences.save()


@receiver(tags_purchased)
def create_tag_group_and_tags(sender, instance: StoreProfile, **kwargs):
    tag_count = kwargs.get(TAG_COUNT)
    if not tag_count:
        raise ValueError("tag_count is required")

    handler = CreateTagsHandler(instance, tag_count)
    handler.handle()
