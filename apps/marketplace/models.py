from decimal import Decimal
import random
import string

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MinLengthValidator

from apps.items.models import Item
from apps.stores.models import Tag
from apps.payments.models.transactions import ItemPaymentTransaction
from apps.marketplace.services.pricing_services import PricingEngine

User = get_user_model()


class BaseItemListing(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    store_commission = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    min_listing_days = models.IntegerField(validators=[MinValueValidator(1)])
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    @property
    def item_price(self):
        return Decimal(self.item.price)

    @property
    def listing_price(self):
        return PricingEngine().calculate_list_price(self.item.price)

    @property
    def transaction_fee(self):
        return PricingEngine().calculate_transaction_fee(self.item.price)

    @property
    def store_commission_amount(self):
        return PricingEngine().calculate_store_commission(
            self.item.price, self.store_commission
        )

    @property
    def member_earnings(self):
        return PricingEngine().calculate_user_earnings(
            self.item.price, self.store_commission
        )

    @property
    def owner(self):
        return self.item.owner

    @property
    def store(self):
        return self.tag.store

    @property
    def item_details(self):
        return self.item

    @staticmethod
    def generate_collection_pin():
        return "".join(random.choices(string.digits, k=2))

    def validate_pin(self, pin):
        return self.collection_pin == pin


class ItemListing(BaseItemListing):
    class Meta:
        db_table = "item_listings"


class RecallReason(models.Model):

    class Type(models.TextChoices):
        ISSUE = "issue", _("Issue")
        STORE_DISCRETION = "store discretion", _("Store Discretion")
        OWNER_REQUEST = "owner request", _("Owner Request")

    reason = models.CharField(max_length=255)
    type = models.CharField(choices=Type.choices, max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recall_reasons"

    def __str__(self):
        return f"{self.reason}"


class RecalledItemListing(BaseItemListing):
    reason = models.ForeignKey(RecallReason, on_delete=models.CASCADE)
    recalled_at = models.DateTimeField(auto_now_add=True)
    collection_pin = models.CharField(
        max_length=2,
        validators=[MinLengthValidator(4)],
        default=BaseItemListing.generate_collection_pin,
        null=False,
    )
    collection_deadline = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recalled_item_listings"

    def __str__(self):
        return f"{self.reason}"


class DelistedItemListing(BaseItemListing):
    reason = models.ForeignKey(RecallReason, on_delete=models.CASCADE)
    delisted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "delisted_item_listings"

    def __str__(self):
        return f"{self.reason}"


class SoldItemListing(BaseItemListing):
    sold_at = models.DateTimeField(auto_now_add=True)
    transaction = models.OneToOneField(
        ItemPaymentTransaction,
        on_delete=models.CASCADE,
        related_name="sold_item_listing",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sold_item_listings"

    def __str__(self):
        return f"{self.buyer}"
