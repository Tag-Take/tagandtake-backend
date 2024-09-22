from celery import shared_task
from django.utils.timezone import now
from apps.notifications.emails.services.email_senders import ListingEmailSender
from apps.marketplace.models import RecalledItemListing


@shared_task
def run_recalled_listing_reminders():
    recalled_listings = RecalledItemListing.objects.all()
    for listing in recalled_listings:
        if is_time_to_remind(listing):
            remind_member.delay(listing.id)


@shared_task
def remind_member(recalled_listing_id):
    recalled_listing = RecalledItemListing.objects.get(id=recalled_listing_id)
    ListingEmailSender.send_collection_reminder_email(recalled_listing)


def is_time_to_remind(recalled_listing: RecalledItemListing):
    return (
        now() < recalled_listing.collection_deadline
        and now().date() != recalled_listing.collection_deadline.date()
        and now().date() != recalled_listing.created_at.date() != now().date()
    )
