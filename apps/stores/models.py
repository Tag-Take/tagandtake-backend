from decimal import Decimal
from pytz import all_timezones

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    MinLengthValidator,
)
from django.utils.translation import gettext_lazy as _
from django.apps import apps

from apps.items.models import ItemCategory, ItemCondition
from apps.stores.utils import generate_pin


User = get_user_model()


class StoreProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="store")
    pin = models.CharField(
        max_length=4,
        validators=[MinLengthValidator(4)],
        default=generate_pin,
        null=False,
    )
    # Store information
    store_name = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    store_bio = models.CharField(max_length=255, blank=True, null=True)
    profile_photo_url = models.URLField(max_length=2048, blank=True, null=True)
    # Socials
    google_profile_url = models.URLField(null=True, blank=True)
    website_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    # Store settings
    commission = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)], default=10
    )
    stock_limit = models.IntegerField(
        blank=False, default=50, null=False, validators=[MinValueValidator(1)]
    )
    min_listing_days = models.IntegerField(
        default=14, validators=[MinValueValidator(7)]
    )
    min_price = models.DecimalField(
        default=0.00,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0.00))],
    )
    currency = models.CharField(max_length=3, default="GBP", null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_profiles"

    def validate_pin(self, pin):
        return self.pin == pin

    @property
    def active_listings_count(self):
        from apps.marketplace.models import Listing

        return Listing.objects.filter(tag__tag_group__store=self).count()

    @property
    def accepting_listings(self):
        return self.active_listings_count < self.stock_limit

    @property
    def remaining_stock(self):
        return self.stock_limit - self.active_listings_count


class StoreAddress(models.Model):
    store = models.OneToOneField(
        StoreProfile, on_delete=models.CASCADE, related_name="store_address"
    )
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_addresses"

    def __str__(self):
        return f"{self.store_profile.store_name} - {self.street_address}, {self.city}, {self.country}"


class StoreOpeningHours(models.Model):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    DAYS_OF_WEEK = [
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday"),
    ]

    store = models.ForeignKey(
        StoreProfile, on_delete=models.CASCADE, related_name="opening_hours"
    )
    day_of_week = models.CharField(max_length=9, choices=DAYS_OF_WEEK)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    timezone = models.CharField(
        max_length=50, choices=[(tz, tz) for tz in all_timezones], default="UTC"
    )
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.day_of_week}: {self.opening_time} - {self.closing_time} ({self.timezone})"

    class Meta:
        db_table = "store_opening_hours"
        verbose_name_plural = "Store Opening Hours"
        unique_together = ("store", "day_of_week")


class StoreNotificationPreferences(models.Model):
    store = models.OneToOneField(
        StoreProfile, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    secondary_email = models.EmailField(blank=True)
    new_listing_notifications = models.BooleanField(default=True)
    sale_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_notification_preferences"

    def __str__(self):
        return f"{self.store.store_name} notification preferences"


class StoreItemCategorie(models.Model):
    store = models.ForeignKey(
        StoreProfile, on_delete=models.CASCADE, related_name="preferred_categories"
    )
    category = models.ForeignKey(
        ItemCategory, on_delete=models.CASCADE, related_name="store_preferences"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_item_categories"

    def __str__(self):
        return f"{self.store.store_name} - {self.category.name}"


class StoreItemConditions(models.Model):
    store = models.ForeignKey(
        StoreProfile, on_delete=models.CASCADE, related_name="preferred_conditions"
    )
    condition = models.ForeignKey(
        ItemCondition, on_delete=models.CASCADE, related_name="store_preferences"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_item_conditions"

    def __str__(self):
        return f"{self.store.store_name} - {self.condition.condition}"


class TagGroup(models.Model):
    store = models.ForeignKey(
        StoreProfile, on_delete=models.CASCADE, related_name="tag_groups"
    )
    group_size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tag_groups"

    def __str__(self):
        return f"{self.store.store_name} - Group of {self.group_size}"


class Tag(models.Model):
    tag_group = models.ForeignKey(
        TagGroup, on_delete=models.CASCADE, related_name="tags"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tags"

    def __str__(self):
        return f"Store: {self.store.store_name} - Tag: {self.id}"

    @property
    def store(self):
        return self.tag_group.store
