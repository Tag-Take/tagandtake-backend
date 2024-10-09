from celery import shared_task

from apps.payments.models.transactions import (
    PendingMemberTransfer,
    PendingStoreTransfer,
)
from apps.payments.services.transfer_services import TransferService


@shared_task
def run_pending_transfers():
    """
    This task ensures that all pending transfers are completed
    """
    pending_member_transfers = PendingMemberTransfer.objects.all()
    for transfer in pending_member_transfers:
        TransferService.run_pending_member_transfer(transfer)

    pending_store_transfers = PendingStoreTransfer.objects.all()
    for transfer in pending_store_transfers:
        TransferService.run_pending_store_transfer(transfer)
