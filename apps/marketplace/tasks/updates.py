from celery import shared_task
from apps.marketplace.services.storage_fee_service import StorageFeeService


@shared_task
def apply_storage_fees_task():
    StorageFeeService.run_storage_fee_checks()
