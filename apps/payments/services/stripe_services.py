from typing import Dict
import json
from django.conf import settings
import stripe
import stripe.checkout
from apps.marketplace.models import ItemListing
from apps.payments.utils import to_stripe_amount
from apps.common.constants import *

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    @staticmethod
    def create_member_stripe_account():
        return stripe.Account.create(
            business_type="individual",
            controller={
                "stripe_dashboard": {
                    "type": "express",
                },
                "fees": {"payer": "application"},
                "losses": {"payments": "application"},
            },
            business_profile={
                "url": "https://www.tagandtake.com",
                "product_description": "Individual Second Hand clothing seller",
            },
            country="gb",
            metadata={
                ACCOUNT_TYPE: MEMBER,
            },
        )

    @staticmethod
    def create_store_stripe_account():
        return stripe.Account.create(
            business_type="company",
            controller={
                "stripe_dashboard": {
                    "type": "express",
                },
                "fees": {"payer": "application"},
                "losses": {"payments": "application"},
            },
            country="gb",
            metadata={
                ACCOUNT_TYPE: STORE,
            },
        )

    @staticmethod
    def create_stripe_account_onboarding_session(connected_account_id: str):
        return stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "account_onboarding": {"enabled": True},
            },
        )

    @staticmethod
    def create_stripe_account_management_session(connected_account_id: str):
        return stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "account_management": {
                    "enabled": True,
                    "features": {"external_account_collection": True},
                },
            },
        )

    @staticmethod
    def create_stripe_account_balances_session(connected_account_id: str):
        return stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "balances": {
                    "enabled": True,
                    "features": {
                        "instant_payouts": True,
                        "standard_payouts": True,
                        "edit_payout_schedule": True,
                    },
                },
            },
        )

    @staticmethod
    def create_stripe_account_notifications_session(connected_account_id: str):
        return stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "notification_banner": {
                    "enabled": True,
                    "features": {"external_account_collection": True},
                },
            },
        )

    def create_stripe_account_payments_session(connected_account_id: str):
        return stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "payments": {
                    "enabled": True,
                    "features": {
                        "refund_management": False,
                        "dispute_management": False,
                        "capture_payments": True,
                    },
                },
            },
        )

    def create_stripe_account_payments_session(connected_account_id: str):
        return stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "payments": {
                    "enabled": True,
                    "features": {
                        "refund_management": False,
                        "dispute_management": False,
                        "capture_payments": True,
                    },
                },
            },
        )

    @staticmethod
    def is_account_fully_onboarded(connected_account_id: str) -> bool:
        account = stripe.Account.retrieve(connected_account_id)
        return account.payouts_enabled

    @staticmethod
    def create_stripe_item_checkout_session(item_listing: ItemListing, tag_id: str):
        metadata = {
            PURCHASE: ITEM,
            ITEM_ID: item_listing.item_details.id,
            ITEM_LISTING_ID: item_listing.id,
            MEMBER_ID: item_listing.owner.id,
            STORE_ID: item_listing.store.id,
            AMOUNT: item_listing.listing_price,
            STORE_AMOUNT: item_listing.store_commission_amount,
            MEMBER_EARNINGS: item_listing.member_earnings,
            TRANSACTION_FEE: item_listing.transaction_fee,
        }
        return stripe.checkout.Session.create(
            ui_mode="embedded",
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "product_data": {"name": item_listing.item_details.name},
                        "unit_amount": to_stripe_amount(item_listing.listing_price),
                    },
                    "quantity": 1,
                },
            ],
            payment_intent_data={METADATA: metadata},
            mode="payment",
            return_url=f"{settings.FRONTEND_URL}/listing/{tag_id}/return?session_id={{CHECKOUT_SESSION_ID}}",
            metadata=metadata,
        )

    @staticmethod
    def create_stripe_supplies_checkout_session(
        line_items: list[Dict[str, str]], store_id: str
    ):
        metadata = {
            PURCHASE: SUPPLIES,
            STORE_ID: store_id,
            LINE_ITEMS: json.dumps(line_items),
        }
        return stripe.checkout.Session.create(
            ui_mode="embedded",
            line_items=line_items,
            payment_intent_data={METADATA: metadata},
            metadata=metadata,
            mode="payment",
            return_url=f"{settings.FRONTEND_URL}/store/supplies/return?session_id={{CHECKOUT_SESSION_ID}}",
        )

    @staticmethod
    def trasfer_to_connected_account(
        account_id: str, amount=str, latest_charge: str = None
    ):
        return stripe.Transfer.create(
            amount=amount,
            currency="gbp",
            source_transaction=latest_charge,
            destination=account_id,
        )

    @staticmethod
    def get_account_type_from_stripe_acct_id(connected_account_id: str):
        account = stripe.Account.retrieve(connected_account_id)
        return account.metadata.get(ACCOUNT_TYPE)

    @staticmethod
    def get_buyer_email_from_payment_intent(payment_intent_id: str):
        checkout_sessions = stripe.checkout.Session.list(
            payment_intent=payment_intent_id
        )
        if checkout_sessions.data:
            return checkout_sessions.data[0].customer_details.email
        return None
