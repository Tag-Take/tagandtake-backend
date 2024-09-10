from django.db import models

from apps.items.models import Item
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store
from apps.payments.models.providers import PaymentProvider


class PaymentTransaction(models.Model):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    TRANSACTION_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="item_transactions"
    )
    buyer = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="buyer_transactions",
        null=True,
        blank=True,
    )
    buyer_email = models.EmailField(null=True, blank=True)
    seller = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="seller_transactions"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    store_commission = models.DecimalField(max_digits=10, decimal_places=2)
    seller_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference_id = models.CharField(max_length=255, blank=True, null=True)
    payment_provider = models.ForeignKey(
        PaymentProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payment_transactions",
    )
    status = models.CharField(
        max_length=10, choices=TRANSACTION_STATUS_CHOICES, default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"

    class Meta:
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        db_table = "payment_transactions"
        ordering = ["-created_at"]


class FailedTransaction(models.Model):
    payment_transaction = models.OneToOneField(
        PaymentTransaction, on_delete=models.CASCADE, related_name="failed_transaction"
    )
    error_message = models.TextField()
    error_code = models.CharField(max_length=255, blank=True, null=True)
    provider_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Failed Transaction {self.payment_transaction.id} - {self.error_message}"
        )

    class Meta:
        verbose_name = "Failed Transaction"
        verbose_name_plural = "Failed Transactions"
        db_table = "failed_transactions"
        ordering = ["-created_at"]
