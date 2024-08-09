from celery import shared_task
from apps.marketplace.services.listing_services import RecalledListingStorageFeeService


@shared_task
def apply_storage_fees_task():
    RecalledListingStorageFeeService.run_storage_fee_checks()
