from django.db import models
from django.contrib.auth import get_user_model
from apps.stores.models import StoreProfile as Store
from apps.members.models import MemberProfile as Member
from apps.items.models import Item


User = get_user_model()


class StripeAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_connect_account_id = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stripe Account for {self.user.email}"

    class Meta:
        verbose_name = "Stripe Account"
        verbose_name_plural = "Stripe Accounts"
        db_table = "stripe_accounts"
        ordering = ["-created_at"]


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
        "items.Item", on_delete=models.CASCADE, related_name="item_transactions"
    )
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="member_transactions"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    store_commission = models.DecimalField(max_digits=10, decimal_places=2)
    seller_earnings = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=255)
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


class Payout(models.Model):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    PAYOUT_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payout_id = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10, choices=PAYOUT_STATUS_CHOICES, default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payout {self.id} - {self.status}"

    class Meta:
        verbose_name = "Payout"
        verbose_name_plural = "Payouts"
        db_table = "payouts"
        ordering = ["-created_at"]
