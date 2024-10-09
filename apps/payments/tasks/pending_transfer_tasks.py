from celery import shared_task
import stripe 
import os


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
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    pending_member_transfers = PendingMemberTransfer.objects.all()
    for transfer in pending_member_transfers:
        TransferService.run_pending_member_transfer(transfer)

    pending_store_transfers = PendingStoreTransfer.objects.all()
    for transfer in pending_store_transfers:
        TransferService.run_pending_store_transfer(transfer)
