from django.db import models


class StoreSupply(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    stripe_price_id = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Store Supply"
        verbose_name_plural = "Store Supplies"
        db_table = "store_supplies"
