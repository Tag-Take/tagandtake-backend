from django.db import models

from apps.payments.models.transactions import SupplyPaymentTransaction


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


class SupplyOrderItem(models.Model):
    order = models.ForeignKey(
        SupplyPaymentTransaction, related_name="supply_order", on_delete=models.CASCADE
    )
    supply = models.ForeignKey(StoreSupply, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.supply.name} - {self.quantity}"

    class Meta:
        verbose_name = "Supply Order Item"
        verbose_name_plural = "Supply Order Items"
        db_table = "supply_order_items"
