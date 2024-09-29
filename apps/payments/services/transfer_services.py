from typing import Any, Dict
import stripe
from apps.payments.models.accounts import MemberPaymentAccount, StorePaymentAccount
from apps.payments.models.transactions import (
    PendingMemberTransfer,
    PendingStoreTransfer,
)
from apps.stores.services.store_services import StoreService
from apps.members.services import MemberService
from apps.payments.utils import to_stripe_amount
from apps.common.constants import (
    ID,
    STORE_AMOUNT,
    METADATA,
    MEMBER_ID,
    LATEST_CHARGE,
    MEMBER_EARNINGS,
    STORE_ID,
)


class TransferService:

    def run_post_success_transfers(event_data_obj: Dict[str, Any]):
        TransferService.post_success_transfer_to_member(event_data_obj)
        TransferService.post_success_transfer_to_store(event_data_obj)

    @staticmethod
    def post_success_transfer_to_member(event_data_obj: Dict[str, Any]):

        try:
            account = TransferService.get_member_payment_account(
                event_data_obj[METADATA][MEMBER_ID]
            )
            stripe_amount = to_stripe_amount(event_data_obj[METADATA][MEMBER_EARNINGS])
            stripe.Transfer.create(
                amount=stripe_amount,
                currency="gbp",
                source_transaction=event_data_obj[LATEST_CHARGE],
                destination=account.stripe_account_id,
            )

        except:
            member = MemberService.get_member(event_data_obj[METADATA][MEMBER_ID])
            PendingMemberTransfer.objects.create(
                member=member,
                amount=event_data_obj[METADATA][MEMBER_EARNINGS],
                payment_intent_id=event_data_obj[ID],
                latest_charge=event_data_obj[LATEST_CHARGE],
            )

    @staticmethod
    def post_success_transfer_to_store(event_data_obj: Dict[str, Any]):

        try:
            account = TransferService.get_store_payment_account(
                event_data_obj[METADATA][STORE_ID]
            )
            stripe_amount = (to_stripe_amount(event_data_obj[METADATA][STORE_AMOUNT]),)
            stripe.Transfer.create(
                amount=stripe_amount,
                currency="gbp",
                source_transaction=event_data_obj[LATEST_CHARGE],
                destination=account.stripe_account_id,
            )
        except:
            store = StoreService.get_store(event_data_obj[METADATA][STORE_ID])
            PendingStoreTransfer.objects.create(
                store=store,
                amount=event_data_obj[METADATA][STORE_AMOUNT],
                payment_intent_id=event_data_obj[ID],
                latest_charge=event_data_obj[LATEST_CHARGE],
            )

    @staticmethod
    def get_member_payment_account(member_id: str):
        return MemberPaymentAccount.objects.get(member__id=member_id)

    def get_store_payment_account(store_id: str):
        return StorePaymentAccount.objects.get(store__id=store_id)
