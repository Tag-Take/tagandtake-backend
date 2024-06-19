from django.dispatch import receiver

from apps.accounts.signals import user_activated
from apps.stores.models import StoreProfile, StoreNotificationPreferences
from apps.accounts.models import User

@receiver(user_activated, sender=User)
def create_store_profile(sender, instance, **kwargs):
    if instance.is_active and instance.role == 'store':
        store_profile, created = StoreProfile.objects.get_or_create(user=instance)
        if created:
            StoreNotificationPreferences.objects.create(store=store_profile)