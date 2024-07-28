from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model

# import min and max value validators
from django.core.validators import MinValueValidator

User = get_user_model()


class Item(models.Model):
    STATUSES = (
        ("available", "Available"),
        ("listed", "Listed"),
        ("recalled", "Recalled"),
        ("sold", "Sold"),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    category = models.ForeignKey(
        "ItemCategory", on_delete=models.CASCADE, related_name="items"
    )
    condition = models.ForeignKey(
        "ItemCondition", on_delete=models.CASCADE, related_name="items"
    )
    status = models.CharField(max_length=255, choices=STATUSES, default="available")
    listed_at = models.DateTimeField(null=True, blank=True)
    sold_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "items"

    def __str__(self):
        return self.name

    @property
    def main_image(self):
        main_image = self.images.order_by("order").first()
        return main_image.image_url if main_image else None

    @property
    def images(self):
        images = self.images.order_by("order").all()
        return images if images else []


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


class ItemImages(models.Model):
    order_choices = [(i, i) for i in range(1, 4)]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    image_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "item_images"

    def __str__(self):
        return self.image
