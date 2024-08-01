from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from decimal import Decimal

User = get_user_model()


class MemberProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_bio = models.CharField(max_length=255, blank=True)
    profile_photo_url = models.URLField(max_length=2048, blank=True, null=True)
    instagram_url = models.URLField(blank=True)
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("-180.00")), MaxValueValidator(Decimal("180.00"))],
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("-90.00")), MaxValueValidator(Decimal("90.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "member_profile"

    @property
    def username(self):
        return self.user.username


class MemberNotificationPreferences(models.Model):
    member = models.OneToOneField(
        MemberProfile, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    secondary_email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    email_notifications = models.BooleanField(default=True)
    mobile_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "member_notification_preferences"

    def __str__(self):
        return f"{self.member.name} notification preferences"
