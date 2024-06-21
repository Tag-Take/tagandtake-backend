from django.db import models


class Item(models.Model):
    class meta:
        db_table = "items"

    STATUS_CHOICES = (
        ("registered", "Registered"),
        ("listed", "Listed"),
        ("recalled", "Recalled"),
    )

    member = models.ForeignKey("members.MemberProfile", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    condition = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="registered")
    

class ItemCategory(models.Model):
    class Meta:
        db_table = "item_categories"

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    category = models.ForeignKey("items.Category", on_delete=models.CASCADE)
  

class Categories(models.Model):
    class Meta:
        db_table = "categories"

    category = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)