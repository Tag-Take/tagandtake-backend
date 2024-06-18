# apps/stores/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import StoreProfile, StoreNotificationPreferences

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_store_profile(sender, instance, created, **kwargs):
    if created:
        StoreProfile.objects.create(user=instance)
        StoreNotificationPreferences.objects.create(store=instance.storeprofile)
