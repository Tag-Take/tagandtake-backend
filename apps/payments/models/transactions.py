from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.items.models import Item
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store


class BaseChekoutSession(models.Model):

    session_id = models.CharField(max_length=255, unique=True)
    payment_intent_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    status = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BasePaymentTransaction(models.Model):

    class PaymentStatuses(models.TextChoices):
        CANCELED = "canceled", _("Cancelled")
        PROCESSING = "processing", _("Processing")
        REQUIRES_ACTION = "requires_action", _("Requires Action")
        REQUIRES_CAPTURE = "requires_capture", _("Requires Capture")
        REQUIRES_CONFIRMATION = "requires_confirmation", _("Requires Confirmation")
        REQUIRES_PAYMENT_METHOD = "requires_payment_method", _(
            "Required Payment Method"
        )
        SUCCEEDED = "succeeded", _("Succeeded")

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    status = models.CharField(max_length=50, choices=PaymentStatuses, null=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseFailedPaymentTransaction(models.Model):
    payment_intent_id = models.CharField(max_length=255)
    error_message = models.TextField()
    error_code = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ItemCheckoutSession(BaseChekoutSession):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="item_checkout_sessions"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_item_checkout_sessions"
    )

    def __str__(self):
        return f"Checkout Session {self.id}"

    class Meta:
        verbose_name = "Item Checkout Session"
        verbose_name_plural = "Item Checkout Sessions"
        db_table = "item_checkout_sessions"


class ItemPaymentTransaction(BasePaymentTransaction):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="item_transactions"
    )
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="item_transactions"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_item_transactions"
    )
    store_commission = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    member_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    buyer_email = models.EmailField(max_length=255, blank=True, null=True)
    latest_charge = models.CharField(max_length=255, unique=True, null=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"

    class Meta:
        verbose_name = "Item Payment Transaction"
        verbose_name_plural = "Item Payment Transactions"
        db_table = "item_payment_transactions"


class FailedItemPaymentTransaction(BaseFailedPaymentTransaction):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="failed_item_transactions"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="failed_item_transactions"
    )

    def __str__(self):
        return f"Failed Item Transaction {self.error_message}"

    class Meta:
        verbose_name = "Failed Item Transaction"
        verbose_name_plural = "Failed Item Transactions"
        db_table = "failed_item_transactions"


class SuppliesCheckoutSession(BaseChekoutSession):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_supply_checkout_sessions"
    )

    def __str__(self):
        return f"Supply Checkout Session {self.id}"

    class Meta:
        verbose_name = "Supply Checkout Session"
        verbose_name_plural = "Supply Checkout Sessions"
        db_table = "supplies_checkout_sessions"


class SuppliesPaymentTransaction(BasePaymentTransaction):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_supply_transactions"
    )

    def __str__(self):
        return f"Supply Transaction {self.id} - {self.status}"

    class Meta:
        verbose_name = "Supply Payment Transaction"
        verbose_name_plural = "Supply Payment Transactions"
        db_table = "supplies_payment_transactions"


class FailedSuppliesPaymentTransaction(BaseFailedPaymentTransaction):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="failed_supply_transactions"
    )

    def __str__(self):
        return f"Failed Supply Transaction - {self.error_message}"

    class Meta:
        verbose_name = "Failed Supply Transaction"
        verbose_name_plural = "Failed Supply Transactions"
        db_table = "failed_supplies_transactions"


class PendingMemberTransfer(models.Model):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="pending_transfers"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_intent_id = models.CharField(max_length=255, unique=True)
    latest_charge = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pending Transfer for {self.member.user.email}"

    class Meta:
        verbose_name = "Pending Member Transfer"
        verbose_name_plural = "Pending Member Transfers"
        db_table = "pending_member_transfers"


class PendingStoreTransfer(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="pending_transfers"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_intent_id = models.CharField(max_length=255, unique=True)
    latest_charge = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pending Transfer for {self.store.store_name}"

    class Meta:
        verbose_name = "Pending Store Transfer"
        verbose_name_plural = "Pending Store Transfers"
        db_table = "pending_store_transfers"
