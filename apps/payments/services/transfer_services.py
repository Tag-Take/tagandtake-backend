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


class TransferHandler:

    def run_post_success_transfers(self, event_data_obj: Dict[str, Any]):
        self.post_success_transfer_to_member(event_data_obj)
        self.post_success_transfer_to_store(event_data_obj)

    @staticmethod
    def post_success_transfer_to_member(event_data_obj: Dict[str, Any]):

        try:
            member_payment_account = MemberPaymentAccount(
                member__id=event_data_obj["metadata"]["member_id"]
            )

            stripe.Transfer.create(
                amount=to_stripe_amount(event_data_obj["metadata"]["member_earnings"]),
                currency="gbp",
                source_transaction=event_data_obj["latest_charge"],
                destination=member_payment_account.stripe_account_id,
            )

        except:
            member = Member.objects.get(id=event_data_obj["metadata"]["member_id"])
            PendingMemberTransfer.objects.create(
                member=member,
                amount=event_data_obj["metadata"]["member_earnings"],
                payment_intent_id=event_data_obj["id"],
                latest_charge=event_data_obj["latest_charge"],
            )

    @staticmethod
    def post_success_transfer_to_store(event_data_obj: Dict[str, Any]):

        try:
            store_payment_account = StorePaymentAccount(
                store__id=event_data_obj["metadata"]["store_id"]
            )

            stripe.Transfer.create(
                amount=to_stripe_amount(event_data_obj["metadata"]["store_amount"]),
                currency="gbp",
                source_transaction=event_data_obj["latest_charge"],
                destination=store_payment_account.stripe_account_id,
            )
        except:
            store = Store.objects.get(id=event_data_obj["metadata"]["store_id"])
            PendingStoreTransfer.objects.create(
                store=store,
                amount=event_data_obj["metadata"]["store_amount"],
                payment_intent_id=event_data_obj["id"],
                latest_charge=event_data_obj["latest_charge"],
            )
