# emails/senders.py

from apps.common.utils.email import send_email
from apps.items.emails.contexts import EmailContextGenerator

class ItemEmailSender:
    @staticmethod
    def send_item_listed_email(listing):
        context_generator = EmailContextGenerator(listing)
        context = context_generator.generate_item_listed_context()
        item = listing.item.name
        send_email(
            subject=f"Item Listed - {item}",
            to=listing.item.owner.email,
            template_name="action_triggered/item_listed.html",
            context=context
        )

    @staticmethod
    def send_item_sold_email(listing, sale_price):
        context_generator = EmailContextGenerator(listing)
        context = context_generator.generate_item_sold_context(sale_price)
        item = listing.item.name
        send_email(
            subject=f"Congratulations! Your Item Sold - {item}",
            to=listing.item.owner.email,
            template_name="action_triggered/item_sold.html",
            context=context
        )

    @staticmethod
    def send_item_recalled_email(listing, recall_reason):
        context_generator = EmailContextGenerator(listing)
        context = context_generator.generate_item_recalled_context(recall_reason)
        item = listing.item.name
        send_email(
            subject=f"Item Recalled - {item}",
            to=listing.item.owner.email,
            template_name="action_triggered/item_recalled.html",
            context=context
        )

    @staticmethod
    def send_item_delisted_email(listing):
        context_generator = EmailContextGenerator(listing)
        context = context_generator.generate_item_delisted_context()
        item = listing.item.name
        send_email(
            subject=f"Item Delisted - {item}",
            to=listing.item.owner.email,
            template_name="action_triggered/item_delisted.html",
            context=context
        )

    @staticmethod
    def send_item_collected_email(listing):
        context_generator = EmailContextGenerator(listing)
        context = context_generator.generate_item_collected_context()
        item = listing.item.name
        send_email(
            subject=f"Item Collected - {item}",
            to=listing.item.owner.email,
            template_name="action_triggered/item_collected.html",
            context=context
        )
