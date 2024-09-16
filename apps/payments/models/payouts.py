from django.db import models

from apps.payments.models.providers import PayoutProvider
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store


class PayoutBase(models.Model):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

    PAYOUT_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=PAYOUT_STATUS_CHOICES, default=PENDING
    )
    stripe_payout_reference_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  
        ordering = ["-created_at"]


class MemberPayout(PayoutBase):
    payout_provider = models.ForeignKey(
        PayoutProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name="member_payouts",
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="payouts")

    def __str__(self):
        return f"Member Payout {self.id} - {self.status} for {self.member.user.email}"

    class Meta:
        verbose_name = "Member Payout"
        verbose_name_plural = "Member Payouts"
        db_table = "member_payouts"


class StorePayout(PayoutBase):
    payout_provider = models.ForeignKey(
        PayoutProvider,
        on_delete=models.SET_NULL,
        null=True,
        related_name="store_payouts",
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="payouts")

    def __str__(self):
        return f"Store Payout {self.id} - {self.status} for {self.store.store_name}"

    class Meta:
        verbose_name = "Store Payout"
        verbose_name_plural = "Store Payouts"
        db_table = "store_payouts"


class FailedPayoutBase(models.Model):
    error_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class MemberFailedPayout(FailedPayoutBase):
    payout = models.ForeignKey(
        MemberPayout, on_delete=models.CASCADE, related_name="failed_member_payout"
    )
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="failed_payouts"
    )

    def __str__(self):
        return f"Failed Payout for {self.member.user.email} - {self.amount}"

    class Meta:
        verbose_name = "Member Failed Payout"
        verbose_name_plural = "Member Failed Payouts"
        db_table = "failed_member_payouts"


class StoreFailedPayout(FailedPayoutBase):
    payout = models.ForeignKey(
        StorePayout, on_delete=models.CASCADE, related_name="failed_store_payout"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="failed_payouts"
    )

    def __str__(self):
        return f"Failed Payout for {self.store.store_name} - {self.amount}"

    class Meta:
        verbose_name = "Store Failed Payout"
        verbose_name_plural = "Store Failed Payouts"
        db_table = "failed_store_payouts"
