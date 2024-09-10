from decimal import Decimal
import random
import string

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError

from apps.items.models import Item
from apps.stores.models import Tag
from apps.members.models import MemberProfile as Member
from apps.marketplace.services.pricing_services import PricingEngine

User = get_user_model()


class BaseListing(models.Model):
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
    def price(self):
        return Decimal(self.item.price)

    @property
    def total_price(self):
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
    def store(self):
        return self.tag.store

    @property
    def item_details(self):
        return self.item

    @staticmethod
    def generate_collection_pin():
        return "".join(random.choices(string.digits, k=2))


class Listing(BaseListing):
    class Meta:
        db_table = "listings"

    def clean(self):
        active_tag_listings = Listing.objects.filter(tag=self.tag)
        if self.pk:
            active_tag_listings = active_tag_listings.exclude(pk=self.pk)
        if active_tag_listings.exists():
            raise ValidationError("There is already an active listing with this tag.")

        active_item_listings = Listing.objects.filter(item=self.item)
        if self.pk:
            active_item_listings = active_item_listings.exclude(pk=self.pk)
        if active_item_listings.exists():
            raise ValidationError("There is already an active listing with this item.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class RecallReason(models.Model):
    ISSUE = "issue"
    STORE_DISCRESSION = "store discretion"
    OWNER_REQUEST = "owner_user request"

    RECALL_REASONS_TYPES = [
        (ISSUE, "Issue"),
        (STORE_DISCRESSION, "Store Discretion"),
        (OWNER_REQUEST, "Owner Request"),
    ]

    reason = models.CharField(max_length=255)
    type = models.CharField(choices=RECALL_REASONS_TYPES, max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recall_reasons"

    def __str__(self):
        return f"{self.reason}"


class RecalledListing(BaseListing):
    reason = models.ForeignKey(RecallReason, on_delete=models.CASCADE)
    recalled_at = models.DateTimeField(auto_now_add=True)
    collection_pin = models.CharField(
        max_length=2,
        validators=[MinLengthValidator(4)],
        default=BaseListing.generate_collection_pin,
        null=False,
    )
    fee_charged_count = models.PositiveIntegerField(default=0)
    last_fee_charge_at = models.DateTimeField(null=True, blank=True)
    last_fee_charge_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
        null=True,
        blank=True,
    )
    next_fee_charge_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recalled_listings"

    def __str__(self):
        return f"{self.reason}"


class DelistedListing(BaseListing):
    reason = models.ForeignKey(RecallReason, on_delete=models.CASCADE)
    delisted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "delisted_listings"

    def __str__(self):
        return f"{self.reason}"


class SoldListing(BaseListing):
    buyer = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    sold_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sold_listings"

    def __str__(self):
        return f"{self.buyer}"
