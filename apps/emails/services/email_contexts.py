from datetime import datetime

from django.contrib.auth.models import User
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from apps.marketplace.services.pricing_services import RECALLED_LISTING_RECURRING_FEE
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store
from apps.marketplace.models import Listing, RecallReason


class AccountEmailContextGenerator:
    def __init__(self, user: User):
        self.user = user

    def generate_account_activation_context(self):
        token = self.generate_activation_token()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        activation_url = f"{settings.FRONTEND_URL}/activate-user/{uid}/{token}/"
        context = {
            "username": self.user.username,
            "activation_url": activation_url,
            "current_year": datetime.now().year,
        }
        return context

    def generate_password_reset_context(self):
        token = self.generate_activation_token()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        reset_url = (
            f"{settings.FRONTEND_URL}/reset-password/confirm?uid={uid}&token={token}"
        )
        context = {
            "username": self.user.username,
            "reset_url": reset_url,
            "current_year": datetime.now().year,
        }
        return context

    def generate_activation_token(self):
        return default_token_generator.make_token(self.user)


class MemberEmailContextGenerator:
    def __init__(self, member: Member):
        self.member = member

    def generate_memeber_welcome_context(self):
        context = {
            "login_url": settings.FRONTEND_URL + settings.LOGIN_ROUTE,
            "how_it_works_url": settings.FRONTEND_URL + settings.HOW_IT_WORKS_ROUTE,
        }
        return context


class StoreEmailContextGenerator:
    def __init__(self, store: Store):
        self.store = store

    def generate_store_welcome_context(self):
        context = {
            "logo_url": settings.LOGO_URL,
            "pin": self.store.pin,
        }
        return context

    def generate_new_store_pin_context(self):
        context = {
            "logo_url": settings.LOGO_URL,
            "pin": self.store.pin,
        }
        return context


class ListingEmailContextGenerator:
    def __init__(self, listing: Listing):
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
        base_context.update(
            {
                "store_name": self.store.shop_name,
                "item_page_url": f"{settings.FRONTEND_URL}/items/{self.item.id}",
            }
        )
        return base_context

    def generate_item_sold_context(self):
        base_context = self.get_base_context()
        sale_price = self.listing.price
        base_context.update(
            {
                "sale_price": sale_price,
                "earnings": self.listing.member_earnings,
            }
        )
        return base_context

    def generate_item_recalled_context(self, recall_reason: RecallReason):
        base_context = self.get_base_context()
        base_context.update(
            {
                "store_name": self.store.shop_name,
                "recall_reason_title": recall_reason.reason,
                "recall_reason_description": recall_reason.description,
                "storage_fee": f"{RECALLED_LISTING_RECURRING_FEE}",
                "item_page_url": f"{settings.FRONTEND_URL}/items/{self.item.id}",
            }
        )
        return base_context

    def generate_item_delisted_context(self):
        base_context = self.get_base_context()
        base_context.update(
            {
                "store_name": self.store.shop_name,
            }
        )
        return base_context

    def generate_item_collected_context(self):
        base_context = self.get_base_context()
        base_context.update(
            {
                "store_name": self.store.shop_name,
            }
        )
        return base_context

    def generate_initial_storage_fee_context(self):
        next_charge_at = self.listing.next_fee_charge_at
        base_context = self.get_base_context()
        base_context.update(
            {
                "store_name": self.store.shop_name,
                "storage_fee": f"{self.listing.last_fee_charge_amount}",
                "next_charge_time": next_charge_at.strftime("%H:%M %p"),
                "next_charge_date": next_charge_at.strftime("%B %d, %Y"),
            }
        )
        return base_context

    def generate_recurring_storage_fee_context(self):
        next_charge_at = self.listing.next_fee_charge_at
        base_context = self.get_base_context()
        base_context.update(
            {
                "store_name": self.store.shop_name,
                "storage_fee": f"{self.listing.last_fee_charge_amount}",
                "fee_count": self.listing.fee_charged_count,
                "next_charge_time": next_charge_at.strftime("%H:%M %p"),
                "next_charge_date": next_charge_at.strftime("%B %d, %Y"),
            }
        )
        return base_context
    
    def generate_collection_reminder_context(self):
        next_charge_at = self.listing.next_fee_charge_at
        base_context = self.get_base_context()
        base_context.update({
            "store_name": self.store.shop_name,
            "recall_reason": self.listing.reason.reason,  
            "next_charge_time": next_charge_at.strftime('%H:%M %p'),
            "next_charge_date": next_charge_at.strftime('%B %d, %Y'),
        })
        return base_context
