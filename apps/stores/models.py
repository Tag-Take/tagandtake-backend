from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField


User = get_user_model()


class StoreProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    post_code = models.CharField(max_length=20, blank=True, null=True)
    secondary_email = models.EmailField(unique=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    opening_hours = JSONField(blank=True, null=True)
    operating_days = JSONField(blank=True, null=True)
    commission = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    stock_limit = models.IntegerField(blank=True, null=True)
    min_listing_days = models.IntegerField(blank=True, null=True)
    min_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    store_description = models.TextField(blank=True, null=True)
    store_logo_url = models.URLField(blank=True, null=True)
    terms_conditions = models.TextField(blank=True, null=True)
    google_analytics_id = models.CharField(max_length=255, blank=True, null=True)
    facebook_pixel_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_profile"


class StoreNotificationPreferences(models.Model):
    store = models.OneToOneField(StoreProfile, on_delete=models.CASCADE)
    sms_notifications = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "store_notification_preferences"


class ShopCategory(models.Model):
    category_id = models.IntegerField()
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shop_category"


class StoreAddress(models.Model):
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "store_address"
