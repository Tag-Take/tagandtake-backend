from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

from apps.items.models import Item
from apps.stores.models import Tag, StoreProfile
from apps.marketplace.services import PricingEngine

User = get_user_model()

# create models for listings that are related to Tags and Items, 
# and listing_issues that is a list og issues that can be reported on a listing
# and recalled items that are items that have been recalled by the store for a issue reason

class Listing(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    stroe_comission = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
        )
    min_listing_days = models.IntegerField(validators=[MinValueValidator(1)])
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        db_table = "listing"

    @property
    def price(self):
        return PricingEngine().calculate_list_price(self.item.price)
    
    @property
    def transaction_fee(self):
        return PricingEngine().calculate_transaction_fee(self.item.price)
    
    @property
    def store_comission_amount(self):
        return PricingEngine().calculate_store_comission(self.item.price, self.store_comission)
    
    @property
    def member_earnings(self):
        return PricingEngine().calculate_user_earnings(self.item.price, self.store_comission)

    @property
    def store(self):
        return self.tag.store

    @property
    def name(self):
        return self.item.name

    @property
    def owner(self):
        return self.item.owner

    @property
    def description(self):
        return self.item.description

    @property
    def size(self):
        return self.item.size

    @property
    def brand(self):
        return self.item.brand

    @property
    def category(self):
        return self.item.category

    @property
    def condition(self):
        return self.item.condition
    

class RecallReason(models.Model):
    RECALL_REASONS_TYPES = [
        ("ISSUE", "Issue"),
        ("STORE DISCRESSION", "Store Discretion"),
        ("OWNER REQUEST", "Owner Request"),
    ]

    reason = models.CharField(max_length=255)
    type = models.CharField(choices=RECALL_REASONS_TYPES, max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recall_reasons"

    def __str__(self):
        return f"{self.issue}"
    

class RecalledItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    store = models.ForeignKey(StoreProfile, on_delete=models.CASCADE)
    min_listing_days = models.IntegerField(validators=[MinValueValidator(1)])
    reason = models.ForeignKey(RecallReason, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recalled_item"

    def __str__(self):
        return f"{self.item.name} - {self.issue.issue}"
    