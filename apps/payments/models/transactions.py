from django.db import models

from apps.items.models import Item
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store
from apps.payments.models.providers import PaymentProvider
from apps.tagandtake.models import StoreSupply


class BasePaymentTransaction(models.Model):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    TRANSACTION_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=TRANSACTION_STATUS_CHOICES, default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseFailedPaymentTransaction(models.Model):
    error_message = models.TextField()
    error_code = models.CharField(max_length=255, blank=True, null=True)
    provider_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ItemPaymentTransaction(BasePaymentTransaction):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="item_transactions"
    )
    buyer_email = models.EmailField(null=True, blank=True)
    seller = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="item_transactions"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_item_transactions"
    )
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name="item_payment_transactions",  
    )

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"

    class Meta:
        verbose_name = "Item Payment Transaction"
        verbose_name_plural = "Item Payment Transactions"
        db_table = "item_payment_transactions"


class FailedItemTransaction(BaseFailedPaymentTransaction):
    payment_transaction = models.OneToOneField(
        ItemPaymentTransaction,
        on_delete=models.CASCADE,
        related_name="failed_item_transaction",
    )

    def __str__(self):
        return f"Failed Item Transaction {self.payment_transaction.id} - {self.error_message}"

    class Meta:
        verbose_name = "Failed Item Transaction"
        verbose_name_plural = "Failed Item Transactions"
        db_table = "failed_item_transaction"


class SupplyPaymentTransaction(BasePaymentTransaction):
    supply = models.ForeignKey(
        StoreSupply, on_delete=models.CASCADE, related_name="supply_transactions"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_supply_transactions"
    )
    quantity = models.IntegerField(default=1)
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name="supply_payment_transactions", 
    )

    def __str__(self):
        return f"Supply Transaction {self.id} - {self.status}"

    class Meta:
        verbose_name = "Supply Payment Transaction"
        verbose_name_plural = "Supply Payment Transactions"
        db_table = "supply_payment_transactions"


class FailedSupplyPaymentTransaction(BaseFailedPaymentTransaction):
    payment_transaction = models.OneToOneField(
        SupplyPaymentTransaction,
        on_delete=models.CASCADE,
        related_name="failed_supply_transaction",
    )

    def __str__(self):
        return f"Failed Supply Transaction {self.payment_transaction.id} - {self.error_message}"

    class Meta:
        verbose_name = "Failed Supply Transaction"
        verbose_name_plural = "Failed Supply Transactions"
        db_table = "failed_supply_transactions"
