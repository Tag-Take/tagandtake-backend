from datetime import datetime

from django.contrib.auth.models import User
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from apps.common.constants import *
from apps.marketplace.services.pricing_services import RECALLED_LISTING_RECURRING_FEE
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store
from apps.marketplace.models import ItemListing, RecallReason, RecalledItemListing


class AccountEmailContextGenerator:
    def __init__(self, user: User):
        self.user = user

    def generate_account_activation_context(self):
        token = self.generate_activation_token()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        activation_url = (
            f"{settings.FRONTEND_URL}/{ACTIVATE}?uuid={uid}&{TOKEN}={token}"
        )
        context = {
            USERNAME: self.user.username,
            ACTIVATION_URL: activation_url,
            CURRENT_YEAR: datetime.now().year,
        }
        return context

    def generate_password_reset_context(self):
        token = self.generate_activation_token()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{CONFIRM}?uid={uid}&{TOKEN}={token}"
        context = {
            USERNAME: self.user.username,
            RESET_URL: reset_url,
            CURRENT_YEAR: datetime.now().year,
        }
        return context

    def generate_activation_token(self):
        return default_token_generator.make_token(self.user)


class MemberEmailContextGenerator:
    def __init__(self, member: Member):
        self.member = member

    def generate_memeber_welcome_context(self):
        context = {
            LOGIN_URL: settings.FRONTEND_URL + settings.LOGIN_ROUTE,
            HOW_IT_WORKS_URL: settings.FRONTEND_URL + settings.HOW_IT_WORKS_ROUTE,
        }
        return context


class StoreEmailContextGenerator:
    def __init__(self, store: Store):
        self.store = store

    def generate_store_welcome_context(self):
        context = {
            LOGO_URL: settings.LOGO_URL,
            PIN: self.store.pin,
        }
        return context

    def generate_new_store_pin_context(self):
        context = {
            LOGO_URL: settings.LOGO_URL,
            PIN: self.store.pin,
        }
        return context


class ListingEmailContextGenerator:
    def get_base_context(self, listing: ItemListing):
        self.item = listing.item
        self.store = listing.store
        self.user = self.item.owner_user
        return {
            USERNAME: self.user.username,
            ITEM_NAME: self.item.name,
            CURRENT_YEAR: datetime.now().year,
        }

    def generate_item_listed_context(self, listing: ItemListing):
        base_context = self.get_base_context(listing)
        base_context.update(
            {
                STORE_NAME: self.store.store_name,
                ITEM_PAGE_URL: f"{settings.FRONTEND_URL}/items/{self.item.id}",
            }
        )
        return base_context

    def generate_item_sold_context(self, listing: ItemListing):
        base_context = self.get_base_context(listing)
        sale_price = listing.item_price
        base_context.update(
            {
                SALE_PRICE: sale_price,
                EARNINGS: listing.member_earnings,
            }
        )
        return base_context

    def generate_item_recalled_context(
        self, listing: ItemListing, recall_reason: RecallReason
    ):
        base_context = self.get_base_context(listing)
        base_context.update(
            {
                STORE_NAME: self.store.store_name,
                RECALL_REASON_TITLE: recall_reason.reason,
                RECALL_REASON_DESCRIPTION: recall_reason.description,
                STORAGE_FEE: f"{RECALLED_LISTING_RECURRING_FEE}",
                ITEM_PAGE_URL: f"{settings.FRONTEND_URL}/items/{self.item.id}",
            }
        )
        return base_context

    def generate_item_delisted_context(self, listing: ItemListing):
        base_context = self.get_base_context(listing)
        base_context.update(
            {
                STORE_NAME: self.store.store_name,
            }
        )
        return base_context

    def generate_item_collected_context(self, recalled_listing: RecalledItemListing):
        base_context = self.get_base_context(recalled_listing)
        base_context.update(
            {
                STORE_NAME: self.store.store_name,
            }
        )
        return base_context

    def generate_initial_storage_fee_context(
        self, recalled_listing: RecalledItemListing
    ):
        next_charge_at = recalled_listing.next_fee_charge_at
        base_context = self.get_base_context(recalled_listing)
        base_context.update(
            {
                STORE_NAME: self.store.store_name,
                STORAGE_FEE: f"{recalled_listing.last_fee_charge_amount}",
                NEXT_CHARGE_TIME: next_charge_at.strftime("%H:%M %p"),
                NEXT_CHARGE_DATE: next_charge_at.strftime("%B %d, %Y"),
            }
        )
        return base_context

    def generate_recurring_storage_fee_context(
        self, recalled_listing: RecalledItemListing
    ):
        next_charge_at = recalled_listing.next_fee_charge_at
        base_context = self.get_base_context(recalled_listing)
        base_context.update(
            {
                STORE_NAME: self.store.store_name,
                STORAGE_FEE: f"{recalled_listing.last_fee_charge_amount}",
                FEE_COUNT: recalled_listing.fee_charged_count,
                NEXT_CHARGE_TIME: next_charge_at.strftime("%H:%M %p"),
                NEXT_CHARGE_DATE: next_charge_at.strftime("%B %d, %Y"),
            }
        )
        return base_context

    def generate_collection_reminder_context(
        self, recalled_listing: RecalledItemListing
    ):
        next_charge_at = recalled_listing.next_fee_charge_at
        base_context = self.get_base_context(recalled_listing)
        base_context.update(
            {
                STORE_NAME: self.store.store_name,
                RECALL_REASON: recalled_listing.reason.reason,
                NEXT_CHARGE_TIME: next_charge_at.strftime("%H:%M %p"),
                NEXT_CHARGE_DATE: next_charge_at.strftime("%B %d, %Y"),
            }
        )
        return base_context

    def generate_new_collection_pin_context(
        self, recalled_listing: RecalledItemListing
    ):
        collection_pin = recalled_listing.collection_pin
        base_context = self.get_base_context(recalled_listing)
        base_context.update({COLLECTION_PIN: collection_pin})
        return base_context
