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
        ordering = ["-created_at"]


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


class MemberWallet(models.Model):
    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet for {self.member.user.email} - Balance: {self.balance}"

    class Meta:
        verbose_name = "Member Wallet"
        verbose_name_plural = "Member Wallets"
        db_table = "member_wallets"
        ordering = ["-created_at"]


class StoreWallet(models.Model):
    store = models.OneToOneField(
        Store, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet for {self.store.user.email} - Balance: {self.balance}"

    class Meta:
        verbose_name = "Store Wallet"
        verbose_name_plural = "Store Wallets"
        db_table = "store_wallets"
        ordering = ["-created_at"]