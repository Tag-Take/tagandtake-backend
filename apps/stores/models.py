from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator, MaxValueValidator, MinLengthValidator
)

from apps.items.models import ItemCategory, ItemCondition
from apps.stores.utils import generate_pin


User = get_user_model()


class StoreProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pin = models.CharField(
        max_length=4, 
        validators=[MinLengthValidator(4)],
        default=generate_pin,
        null=False
    )
    # Basic store information
    shop_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    store_bio = models.CharField(max_length=255)
    profile_photo_url = models.URLField(blank=True, null=True)
    # Socials
    google_profile_url = models.URLField(null=True, blank=True)  
    website_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    # Payment details
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    commission = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        default=10
    )
    # Store settings
    stock_limit = models.IntegerField(blank=True, default=50, null=True)
    active_tags_count = models.IntegerField(default=0)  # (keep <= stock limit)
    min_listing_days = models.IntegerField(
        default=14,
        validators=[MinValueValidator(7)]
    )
    min_price = models.DecimalField(
        default=0.00,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_profiles"


class StoreNotificationPreferences(models.Model):
    store = models.OneToOneField(StoreProfile, on_delete=models.CASCADE, related_name='notification_preferences')
    secondary_email = models.EmailField(blank=True)  
    new_listing_notifications = models.BooleanField(default=True)
    sale_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_notification_preferences"

    def __str__(self):
        return f'{self.store.shop_name} notification preferences'
    

class StoreItemCategorie(models.Model):
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE, related_name='preferred_categories')
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, related_name='store_preferences')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_item_categories"

    def __str__(self):
        return f'{self.store.shop_name} - {self.category.name}'
    

class StoreItemConditions(models.Model):
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE, related_name='preferred_conditions')
    condition = models.ForeignKey(ItemCondition, on_delete=models.CASCADE, related_name='store_preferences')
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
        db_table = "tag_groups"

    def __str__(self):
        return f'{self.store.shop_name} - Group of {self.group_size}'


class Tag(models.Model):
    tag_group = models.ForeignKey(TagGroup, on_delete=models.CASCADE, related_name='tags')
    hash = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tags"

    def __str__(self):
        return f'Store: {self.store.shop_name} - Tag: {self.hash}'

    @property
    def store(self):
        return self.tag_group.store