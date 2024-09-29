from django.db import models

from apps.payments.models.transactions import (
    SuppliesPaymentTransaction,
    SuppliesCheckoutSession,
)
from apps.stores.models import StoreProfile as Store


class StoreSupply(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Store Supply"
        verbose_name_plural = "Store Supplies"
        db_table = "store_supplies"


class SupplyCheckoutItem(models.Model):
    checkout_session = models.ForeignKey(
        SuppliesCheckoutSession, on_delete=models.CASCADE
    )
    supply = models.ForeignKey(StoreSupply, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.checkout_session} - {self.item} (x{self.quantity})"

    class Meta:
        verbose_name = "Supply Checkout Item"
        verbose_name_plural = "Supply Checkout Items"
        db_table = "supply_checkout_items"


class SupplyOrderItem(models.Model):
    order = models.ForeignKey(
        SuppliesPaymentTransaction,
        related_name="supply_order",
        on_delete=models.CASCADE,
    )
    store = (
        models.ForeignKey(
            Store, on_delete=models.CASCADE, related_name="store_supply_order"
        ),
    )
    supply = models.ForeignKey(StoreSupply, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.supply.name} - {self.quantity}"

    class Meta:
        verbose_name = "Supply Order Item"
        verbose_name_plural = "Supply Order Items"
        db_table = "supply_order_items"
