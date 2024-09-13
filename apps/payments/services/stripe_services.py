from django.conf import settings
import stripe
from apps.payments.models.accounts import StorePaymentAccount, MemberPaymentAccount

stripe.api_key = settings.STRIPE_SECRET_KEY


def transfer_funds_to_store(event):
    session = event['data']['object']
    metadata = event['data']['object']['metadata']    

    store_amount = metadata["store_amount"]
    store_id = metadata["store_id"]
    payment_intent_id = session['payment_intent']

    store_payment_account = StorePaymentAccount(store__id = store_id)
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

    stripe.Transfer.create(
        amount = store_amount,
        currency = "gbp",
        source_transaction = payment_intent['latest_charge'],
        destination = store_payment_account.stripe_account_id,
    )

def transfer_funds_to_member(event):
    session = event['data']['object']
    metadata = event['data']['object']['metadata']    

    member_amount = metadata["member_amount"]
    member_id = metadata["member_id"]
    payment_intent_id = session['payment_intent']

    member_payment_account = MemberPaymentAccount(member__id = member_id)
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

    stripe.Transfer.create(
        amount = member_amount,
        currency = "gbp",
        source_transaction = payment_intent['latest_charge'],
        destination = member_payment_account.stripe_account_id,
    )



