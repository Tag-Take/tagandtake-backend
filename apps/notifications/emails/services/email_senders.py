# emails/senders.py
from django.contrib.auth import get_user_model

from apps.common.constants import ACTION_TRIGGERED, NOTIFICATIONS, REMINDERS
from apps.notifications.emails.services.email_service import send_email
from apps.notifications.emails.services.email_contexts import (
    AccountEmailContextGenerator,
    MemberEmailContextGenerator,
    StoreEmailContextGenerator,
    ListingEmailContextGenerator,
)
from apps.accounts.models import User
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store
from apps.marketplace.models import ItemListing, RecalledItemListing


class AccountEmailSender:
    def __init__(self, user: User):
        self.user = user

    def send_activation_email(self):
        context_generator = AccountEmailContextGenerator(self.user)
        context = context_generator.generate_account_activation_context()
        if self.user.role == User.Roles.MEMBER:
            template_name = f"{ACTION_TRIGGERED}/member_activate.html"
        elif self.user.role == User.Roles.STORE:
            template_name = f"{ACTION_TRIGGERED}/store_activate.html"

        send_email(
            subject="Activate your account",
            to=self.user.email,
            template_name=template_name,
            context=context,
        )

    def send_password_reset_email(self):
        context_generator = AccountEmailContextGenerator(self.user)
        context = context_generator.generate_password_reset_context()
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
            template_name=f"{ACTION_TRIGGERED}/member_welcome.html",
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
            template_name=f"{ACTION_TRIGGERED}/store_welcome.html",
            context=context,
        )

    def send_reset_pin_email(self):
        context_generator = StoreEmailContextGenerator(self.store)
        context = context_generator.generate_store_welcome_context()
        send_email(
            subject="New Tag&Take Store PIN",
            to=self.store.user.email,
            template_name=f"{ACTION_TRIGGERED}/store_new_pin.html",
            context=context,
        )


class ListingEmailSender(ListingEmailContextGenerator):

    def send_listing_created_email(listing: ItemListing):
        context_generator = ListingEmailContextGenerator()
        context = context_generator.generate_item_listed_context(listing)
        item = listing.item.name
        send_email(
            subject=f"Item Listed - {item}",
            to=listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_listed.html",
            context=context,
        )

    def send_listing_sold_email(listing: ItemListing):
        context_generator = ListingEmailContextGenerator()
        context = context_generator.generate_item_sold_context(listing)
        item = listing.item.name
        send_email(
            subject=f"Congratulations! Your Item Sold - {item}",
            to=listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_sold.html",
            context=context,
        )

    def send_listing_recalled_email(listing: ItemListing, recall_reason: int):
        context_generator = ListingEmailContextGenerator()
        context = context_generator.generate_item_recalled_context(
            listing, recall_reason
        )
        item = listing.item.name
        send_email(
            subject=f"Item Recalled - {item}",
            to=listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_recalled.html",
            context=context,
        )

    def send_listing_delisted_email(listing: ItemListing):
        context_generator = ListingEmailContextGenerator()
        context = context_generator.generate_item_delisted_context(listing)
        item = listing.item.name
        send_email(
            subject=f"Item Delisted - {item}",
            to=listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_delisted.html",
            context=context,
        )

    def send_recalled_listing_collected_email(recalled_listing: RecalledItemListing):
        context_generator = ListingEmailContextGenerator()
        context = context_generator.generate_item_collected_context(recalled_listing)
        item = recalled_listing.item.name
        send_email(
            subject=f"Collection Confirmation - {item}",
            to=recalled_listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/item_collected.html",
            context=context,
        )

    def send_item_abandonded_email(recalled_listing: RecalledItemListing):
        context_generator = ListingEmailContextGenerator()
        context = context_generator.generate_item_abandonded_context(recalled_listing)
        item = recalled_listing.item.name
        send_email(
            subject=f"Notice: Item Was Not Collected - {item}",
            to=recalled_listing.item.owner.email,
            template_name=f"{NOTIFICATIONS}/item_abandoned_notification.html",
            context=context,
        )

    def send_collection_reminder_email(recalled_listing: RecalledItemListing):
        context_generator = ListingEmailContextGenerator()
        context = context_generator.generate_collection_reminder_context(
            recalled_listing
        )
        item = recalled_listing.item.name
        send_email(
            subject=f"Collection Reminder - {item}",
            to=recalled_listing.item.owner.email,
            template_name=f"{REMINDERS}/collect_item_reminder.html",
            context=context,
        )

    def send_new_collection_pin_email(recalled_listing):
        context_generator = ListingEmailContextGenerator()
        context = context_generator.generate_new_collection_pin_context(
            recalled_listing
        )
        item = recalled_listing.item.name
        send_email(
            subject=f"New Collection PIN - {item}",
            to=recalled_listing.item.owner.email,
            template_name=f"{ACTION_TRIGGERED}/new_collection_pin.html",
            context=context,
        )
