from django.db import models

from apps.items.models import Item
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store
from apps.payments.models.providers import PaymentProvider


class BaseChekoutSession(models.Model):

    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BasePaymentTransaction(models.Model):
    CANCELED = "canceled"
    PROCESSING = "processing"
    REQUIRES_ACTION = "requires_action"
    REQUIRES_CAPTURE = "requires_capture"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_PAYMENT_METHOD = "requires_payment_method"
    SUCCEEDED = "succeeded"

    PAYMENT_STAUSES = (
        (CANCELED, "Cancelled"),
        (PROCESSING, "Procession"),
        (REQUIRES_ACTION, "Requires Action"),
        (REQUIRES_CAPTURE, "Requires Capture"),
        (REQUIRES_CONFIRMATION, "Requires Confirmation"),
        (REQUIRES_PAYMENT_METHOD, "Required Payment Method"),
        (SUCCEEDED, "Succeeded"),
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_intent_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STAUSES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseFailedPaymentTransaction(models.Model):
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
    buyer_email = models.EmailField(null=True, blank=True)
    seller = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="item_transactions"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_item_transactions"
    )

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"

    class Meta:
        verbose_name = "Item Payment Transaction"
        verbose_name_plural = "Item Payment Transactions"
        db_table = "item_payment_transactions"


class FailedItemPaymentTransaction(BaseFailedPaymentTransaction):
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
    payment_transaction = models.OneToOneField(
        SuppliesPaymentTransaction,
        on_delete=models.CASCADE,
        related_name="failed_supplies_transaction",
    )

    def __str__(self):
        return f"Failed Supply Transaction {self.payment_transaction.id} - {self.error_message}"

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
