from apps.payments.models.accounts import MemberPaymentAccount, StorePaymentAccount
from apps.payments.services.stripe_services import StripeService
from apps.accounts.models import User


class PaymentAccountService:
    @staticmethod
    def get_or_create_payment_account(user):
        if user.role == User.Roles.MEMBER:
            return MemberPaymentAccountService.get_or_create_member_payment_account(
                user.member
            )
        elif user.role == User.Roles.STORE:
            return StorePaymentAccountService.get_or_create_store_payment_account(
                user.store
            )
        else:
            raise ValueError("Unknown user role")


class MemberPaymentAccountService:
    @staticmethod
    def get_member_payment_account(member):
        return MemberPaymentAccount.objects.get(member=member)

    @staticmethod
    def get_or_create_member_payment_account(member):
        try:
            return MemberPaymentAccount.objects.get(member=member)
        except MemberPaymentAccount.DoesNotExist:
            stripe_account = StripeService.create_member_stripe_account()
            return MemberPaymentAccount.objects.create(
                member=member,
                stripe_account_id=stripe_account.id,
            )


class StorePaymentAccountService:
    @staticmethod
    def get_store_payment_account(store):
        return StorePaymentAccount.objects.get(store=store)

    @staticmethod
    def get_or_create_store_payment_account(store):
        try:
            return StorePaymentAccount.objects.get(store=store)
        except StorePaymentAccount.DoesNotExist:
            stripe_account = StripeService.create_store_stripe_account()
            return StorePaymentAccount.objects.create(
                store=store,
                stripe_account_id=stripe_account.id,
            )
