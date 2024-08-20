from celery import shared_task
from apps.marketplace.services.listing_services import RecalledListingCollectionReminderService


@shared_task
def run_storage_fee_reminder_checks():
    RecalledListingCollectionReminderService.run_storage_fee_reminder_checks()
