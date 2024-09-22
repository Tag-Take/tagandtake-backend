from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from apps.members.models import MemberProfile as Member
from apps.common.constants import ITEMS, ORDER, IMAGES

User = get_user_model()


class ItemCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "item_categories"

    def __str__(self):
        return self.name


class ItemCondition(models.Model):
    condition = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "item_conditions"

    def __str__(self):
        return self.condition


class Item(models.Model):
    class Statuses(models.TextChoices):
        AVAILABLE = "available", _("Available")
        LISTED = "listed", _("Listed")
        RECALLED = "recalled", _("Recalled")
        SOLD = "sold", _("Sold")
        ABANDONED = "abandoned", _("Abandoned")

    owner = models.ForeignKey(Member, on_delete=models.CASCADE, related_name=ITEMS)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    category = models.ForeignKey(
        ItemCategory, on_delete=models.CASCADE, related_name=ITEMS
    )
    condition = models.ForeignKey(
        ItemCondition, on_delete=models.CASCADE, related_name=ITEMS
    )
    status = models.CharField(
        max_length=255, choices=Statuses.choices, default=Statuses.AVAILABLE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = ITEMS

    def __str__(self):
        return self.name

    @property
    def owner_user(self):
        return self.owner.user

    @property
    def main_image(self):
        main_image = self.images.order_by(ORDER).first()
        return main_image.image_url if main_image else None

    @property
    def images(self):
        images = self.images.order_by(ORDER).all()
        return images if images else []

    @property
    def category_details(self):
        return self.category

    @property
    def condition_details(self):
        return self.condition


class ItemImages(models.Model):
    order_choices = [(i, i) for i in range(1, 4)]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name=IMAGES)
    image_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "item_images"

    def __str__(self):
        return self.image
