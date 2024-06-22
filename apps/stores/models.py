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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_profile"


class StoreNotificationPreferences(models.Model):
    store = models.OneToOneField(StoreProfile, on_delete=models.CASCADE, related_name='notification_preferences')
    sms_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_notification_preferences"

    def __str__(self):
        return f'{self.store.shop_name} Preferences'


class StoreCategories(models.Model):
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE, related_name='preferred_categories')
    category = models.ForeignKey('items.ItemCategory', on_delete=models.CASCADE, related_name='store_preferences')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_categories"

    def __str__(self):
        return f'{self.store.shop_name} - {self.category.name}'
    

class StoreItemConditions(models.Model):
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE, related_name='preferred_conditions')
    condition = models.ForeignKey('items.ItemCondition', on_delete=models.CASCADE, related_name='store_preferences')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_item_conditions"

    def __str__(self):
        return f'{self.store.shop_name} - {self.condition.condition}'


class TagGroup(models.Model):
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE, related_name='tag_groups')
    group_size = models.IntegerField()
    activated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tag_group"

    def __str__(self):
        return f'{self.store.shop_name} - Group of {self.group_size}'


class Tag(models.Model):
    tag_group = models.ForeignKey(TagGroup, on_delete=models.CASCADE, related_name='tags')
    hash = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tag"

    def __str__(self):
        return f'Tag {self.hash}'
