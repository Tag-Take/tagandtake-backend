from django.db import models

class Item(models.Model):
    STATUSES = (
        ("available", "Available"),
        ("listed", "Listed"),
        ("recalled", "Recalled"),
        ("sold", "Sold"),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    category = models.ForeignKey(
        "ItemCategory", on_delete=models.CASCADE, related_name="items"
    )
    condition = models.ForeignKey(
        "ItemCondition", on_delete=models.CASCADE, related_name="items"
    )
    status = models.CharField(max_length=255, choices=STATUSES, default="available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "items"

    def __str__(self):
        return self.name

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
