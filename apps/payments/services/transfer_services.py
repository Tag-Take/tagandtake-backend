from typing import Any, Dict
import stripe
from apps.payments.models.accounts import MemberPaymentAccount, StorePaymentAccount
from apps.payments.models.transactions import (
    PendingMemberTransfer,
    PendingStoreTransfer,
)
from apps.members.models import MemberProfile as Member 
from apps.stores.models import StoreProfile as Store
from apps.payments.services.stripe_services import StripeService
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

    @staticmethod
    def run_post_success_transfers(event_data_obj: Dict[str, Any]):
        TransferService.post_success_transfer_to_member(event_data_obj)
        TransferService.post_success_transfer_to_store(event_data_obj)

    @staticmethod
    def run_pending_member_transfer(pending_transfer: PendingMemberTransfer): 
        try:
            account = TransferService.get_store_payment_account(
                pending_transfer.member
            ) 
            amount = to_stripe_amount(pending_transfer.amount)
            transfer = StripeService.trasfer_to_connected_account(
                account.stripe_account_id, amount, pending_transfer.latest_charge
            )
        except: 
            # TODO: implement this 
            pass


    @staticmethod
    def run_pending_member_transfer(pending_transfer: PendingMemberTransfer): 
        try: 
            account = TransferService.get_store_payment_account(
                pending_transfer.member
            ) 
            amount = to_stripe_amount(pending_transfer.amount)
            transfer = StripeService.trasfer_to_connected_account(
                account.stripe_account_id, amount, pending_transfer.latest_charge
            )
        except: 
            # TODO: implement this 
            pass

    @staticmethod
    def post_success_transfer_to_member(event_data_obj: Dict[str, Any]):

        try:
            account = TransferService.get_member_payment_account(
                event_data_obj[METADATA][MEMBER_ID]
            )
            amount = to_stripe_amount(event_data_obj[METADATA][MEMBER_EARNINGS])
            latest_charge = event_data_obj[LATEST_CHARGE]
            transfer = StripeService.trasfer_to_connected_account(
                account.stripe_account_id, amount, latest_charge
            )

        except:
            member = MemberService.get_member(event_data_obj[METADATA][MEMBER_ID])
            amount=event_data_obj[METADATA][MEMBER_EARNINGS]
            payment_intent_id=event_data_obj[ID]
            latest_charge=event_data_obj[LATEST_CHARGE]            
            TransferService.create_pending_member_trasnfer(
                member=member,
                amount=amount,
                payment_intent_id=payment_intent_id,
                latest_charge=latest_charge,
            )

    @staticmethod
    def post_success_transfer_to_store(event_data_obj: Dict[str, Any]):

        try:
            account = TransferService.get_store_payment_account(
                event_data_obj[METADATA][STORE_ID]
            )
            stripe_amount = to_stripe_amount(event_data_obj[METADATA][STORE_AMOUNT])
            stripe.Transfer.create(
                amount=stripe_amount,
                currency="gbp",
                source_transaction=event_data_obj[LATEST_CHARGE],
                destination=account.stripe_account_id,
            )
        except:
            store = StoreService.get_store(event_data_obj[METADATA][STORE_ID])
            amount=event_data_obj[METADATA][STORE_AMOUNT]
            payment_intent_id=event_data_obj[ID]
            latest_charge=event_data_obj[LATEST_CHARGE]
            TransferService.create_pending_store_trasnfer(
                store, amount, payment_intent_id, latest_charge
            )          

    @staticmethod
    def get_member_payment_account(member_id: str):
        return MemberPaymentAccount.objects.get(member__id=member_id)

    def get_store_payment_account(store_id: str):
        return StorePaymentAccount.objects.get(store__id=store_id)
    
    def create_pending_member_trasnfer(
            member: Member, amount: str, payment_intent_id: str, latest_charge: str
        ): 
        PendingMemberTransfer.objects.create(
            member=member,
            amount=amount,
            payment_intent_id=payment_intent_id,
            latest_charge=latest_charge,
        )

    def create_pending_store_trasnfer(
            store: Store, amount: str, payment_intent_id: str, latest_charge: str
        ): 
        PendingStoreTransfer.objects.create(
            store=store,
            amount=amount,
            payment_intent_id=payment_intent_id,
            latest_charge=latest_charge,
        )
