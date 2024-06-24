from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "member_profile"


class MemberNotificationPreferences(models.Model):
    member = models.OneToOneField(
        MemberProfile, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    secondary_email = models.EmailField(blank=True)
    new_listing_notifications = models.BooleanField(default=True)
    sale_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "member_notification_preferences"

    def __str__(self):
        return f"{self.member.name} notification preferences"
