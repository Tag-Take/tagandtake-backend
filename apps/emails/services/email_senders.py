# emails/senders.py
from apps.common.utils.constants import ACTION_TRIGGERED, NOTIFICATIONS
from apps.emails.services.email_service import send_email
from apps.emails.services.email_contexts import (
    AccountEmailContextGenerator,
    MemberEmailContextGenerator,
    StoreEmailContextGenerator,
    ListingEmailContextGenerator,
)
from apps.accounts.models import User
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store
from apps.marketplace.models import Listing


class AccountEmailSender:
    def __init__(self, user: User):
        self.user = user

    def send_activation_email(self):
        context_generator = AccountEmailContextGenerator(self.user)
        context = context_generator.generate_account_activation_context()
        send_email(
            subject="Activate your account",
            to=self.user.email,
            template_name=f"{ACTION_TRIGGERED}/account_activate.html",
            context=context,
        )

    def send_password_reset_email(self):
        context_generator = AccountEmailContextGenerator(self.user)
        context = context_generator.generate_password_reset_context(self.user)
        send_email(
            subject="Password Reset Request",
            to=self.user.email,
            template_name=f"{ACTION_TRIGGERED}/account_password_reset.html",
            context=context,
        )


class MemberEmailSender:
    def __init__(self, member: Member):
        self.member = member

    def send_welcome_email(self):
        context_generator = MemberEmailContextGenerator(self.member)
        context = context_generator.generate_memeber_welcome_context()
        send_email(
            subject="Welcome to Tag&Take!",
            to=self.member.user.email,
            template_name=f"{ACTION_TRIGGERED}/welcome_email.html",
            context=context,
        )


class StoreEmailSender:
    def __init__(self, store: Store):
        self.store = store

    def send_welcome_email(self):
        context_generator = StoreEmailContextGenerator(self.store)
        context = context_generator.generate_store_welcome_context()
        send_email(
            subject="Welcome to Tag&Take",
            to=self.store.user.email,
            template_name=f"{ACTION_TRIGGERED}/send_pin.html",
            context=context,
        )

    def send_reset_pin_email(self):
        context_generator = StoreEmailContextGenerator(self.store)
        context = context_generator.generate_store_welcome_context()
        send_email(
            subject="New Tag&Take Store PIN",
            to=self.store.user.email,
            template_name=f"{ACTION_TRIGGERED}/resend_pin.html",
            context=context,
        )


class ItemEmailSender:
    def __init__(self, listing: Listing):
        self.listing = listing

    def send_item_listed_email(self):
        context_generator = ListingEmailContextGenerator(self.listing)
        context = context_generator.generate_item_listed_context()
        item = self.listing.item.name
        send_email(
            subject=f"Item Listed - {item}",
            to=self.listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_listed.html",
            context=context,
        )

    def send_item_sold_email(self, sale_price: str):
        context_generator = ListingEmailContextGenerator(self.listing)
        context = context_generator.generate_item_sold_context(sale_price)
        item = self.listing.item.name
        send_email(
            subject=f"Congratulations! Your Item Sold - {item}",
            to=self.listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_sold.html",
            context=context,
        )

    def send_item_recalled_email(self, recall_reason: int):
        context_generator = ListingEmailContextGenerator(self.listing)
        context = context_generator.generate_item_recalled_context(recall_reason)
        item = self.listing.item.name
        send_email(
            subject=f"Item Recalled - {item}",
            to=self.listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_recalled.html",
            context=context,
        )

    def send_item_delisted_email(self):
        context_generator = ListingEmailContextGenerator(self.listing)
        context = context_generator.generate_item_delisted_context()
        item = self.listing.item.name
        send_email(
            subject=f"Item Delisted - {item}",
            to=self.listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_delisted.html",
            context=context,
        )

    def send_item_collected_email(self):
        context_generator = ListingEmailContextGenerator(self.listing)
        context = context_generator.generate_item_collected_context()
        item = self.listing.item.name
        send_email(
            subject=f"Collection Confirmation - {item}",
            to=self.listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_collected.html",
            context=context,
        )

    def send_storage_fee_charged_email(self):
        context_generator = ListingEmailContextGenerator(self.listing)
        item = self.listing.item.name

        if self.listing.fee_charged_count == 1:
            context = context_generator.generate_initial_storage_fee_context()
            send_email(
                subject=f"Storage Fee Charged - {item}",
                to=self.listing.item.owner.email,
                template_name=f"{NOTIFICATIONS}/initial_storage_fee_charged.html",
                context=context,
            )
        elif self.listing.fee_charged_count > 1:
            context = context_generator.generate_recurring_storage_fee_context()
            send_email(
                subject=f"Recurring Storage Fee Charged - {item}",
                to=self.listing.item.owner.email,
                template_name=f"{NOTIFICATIONS}/recurring_storage_fee_charged.html",
                context=context,
            )
