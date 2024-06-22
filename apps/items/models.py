from django.db import models


class ItemCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "item_category"

    def __str__(self):
        return self.name

class ItemCondition(models.Model):
    condition = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "item_condition"

    def __str__(self):
        return self.condition
