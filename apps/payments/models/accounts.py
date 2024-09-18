from django.db import models
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store


class PaymentAccountBase(models.Model):
    stripe_account_id = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MemberPaymentAccount(PaymentAccountBase):
    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="payment_account"
    )

    def __str__(self):
        return f"Member Payment Account for {self.member.user.email} ({self.provider})"

    class Meta:
        verbose_name = "Member Payment Account"
        verbose_name_plural = "Member Payment Accounts"
        db_table = "member_payment_accounts"


class StorePaymentAccount(PaymentAccountBase):
    store = models.OneToOneField(
        Store, on_delete=models.CASCADE, related_name="payment_account"
    )

    def __str__(self):
        return f"Store Payment Account for {self.store.store_name} ({self.provider})"

    class Meta:
        verbose_name = "Store Payment Account"
        verbose_name_plural = "Store Payment Accounts"
        db_table = "store_payment_accounts"
