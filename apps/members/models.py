from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    profile_photo_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # Added field for user location
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'member_profile'


class MemberNotificationPreferences(models.Model):
    member = models.OneToOneField(MemberProfile, on_delete=models.CASCADE)
    sms_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'member_notification_preferences'
