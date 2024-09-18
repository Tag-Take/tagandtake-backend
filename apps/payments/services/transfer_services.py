from typing import Any, Dict
import stripe
from decimal import Decimal
from apps.payments.models.accounts import MemberPaymentAccount, StorePaymentAccount
from apps.payments.models.transactions import (
    PendingMemberTransfer,
    PendingStoreTransfer,
)
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store
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


class TransferHandler:

    def run_post_success_transfers(self, event_data_obj: Dict[str, Any]):
        self.post_success_transfer_to_member(event_data_obj)
        self.post_success_transfer_to_store(event_data_obj)

    @staticmethod
    def post_success_transfer_to_member(event_data_obj: Dict[str, Any]):

        try:
            member_payment_account = MemberPaymentAccount(
                member__id=event_data_obj[METADATA][MEMBER_ID]
            )

            stripe.Transfer.create(
                amount=to_stripe_amount(event_data_obj[METADATA][MEMBER_EARNINGS]),
                currency="gbp",
                source_transaction=event_data_obj[LATEST_CHARGE],
                destination=member_payment_account.stripe_account_id,
            )

        except:
            member = Member.objects.get(id=event_data_obj[METADATA][MEMBER_ID])
            PendingMemberTransfer.objects.create(
                member=member,
                amount=event_data_obj[METADATA][MEMBER_EARNINGS],
                payment_intent_id=event_data_obj[ID],
                latest_charge=event_data_obj[LATEST_CHARGE],
            )

    @staticmethod
    def post_success_transfer_to_store(event_data_obj: Dict[str, Any]):

        try:
            store_payment_account = StorePaymentAccount(
                store__id=event_data_obj[METADATA][STORE_ID]
            )

            stripe.Transfer.create(
                amount=to_stripe_amount(event_data_obj[METADATA][STORE_AMOUNT]),
                currency="gbp",
                source_transaction=event_data_obj[LATEST_CHARGE],
                destination=store_payment_account.stripe_account_id,
            )
        except:
            store = Store.objects.get(id=event_data_obj[METADATA][STORE_ID])
            PendingStoreTransfer.objects.create(
                store=store,
                amount=event_data_obj[METADATA][STORE_AMOUNT],
                payment_intent_id=event_data_obj[ID],
                latest_charge=event_data_obj[LATEST_CHARGE],
            )
