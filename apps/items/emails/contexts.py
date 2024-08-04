# emails/contexts.py

from datetime import datetime
from django.conf import settings
from apps.marketplace.pricing import PricingEngine

class EmailContextGenerator:
    def __init__(self, listing):
        self.listing = listing
        self.item = listing.item
        self.store = listing.store
        self.user = self.item.owner

    def get_base_context(self):
        return {
            "username": self.user.username,
            "item_name": self.item.name,
            "current_year": datetime.now().year,
        }

    def generate_item_listed_context(self):
        base_context = self.get_base_context()
        base_context.update({
            "store_name": self.store.shop_name,
            "item_page_url": f"{settings.FRONTEND_URL}/items/{self.item.id}",
        })
        return base_context

    def generate_item_sold_context(self, sale_price):
        base_context = self.get_base_context()
        base_context.update({
            "sale_price": sale_price,
            "earnings": self.listing.member_earnings,
        })
        return base_context

    def generate_item_recalled_context(self, recall_reason):
        base_context = self.get_base_context()
        base_context.update({
            "store_name": self.store.shop_name,
            "recall_reason_title": recall_reason.reason,
            "recall_reason_description": recall_reason.description,
            "storage_fee": f"£{PricingEngine.storage_fee}",
            "item_page_url": f"{settings.FRONTEND_URL}/items/{self.item.id}",
        })
        return base_context

    def generate_item_delisted_context(self):
        return self.get_base_context()

    def generate_item_collected_context(self):
        base_context = self.get_base_context()
        base_context.update({
            "store_name": self.store.shop_name,
        })
        return base_context
