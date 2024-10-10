import stripe 
import os 

from celery import shared_task

from apps.payments.models.transactions import (
    ItemCheckoutSession, 
    ItemPaymentTransaction
)
from apps.payments.stripe_events.platform_events.payment_intent_handlers import PaymentIntentSucceededHandler


@shared_task
def run_item_transaction_cleanup():
    """
    This task ensures that all transactions that should exist do exist
    """
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    checkouts = ItemCheckoutSession.objects.filter(checkout_status_checked=False)
    for checkout in checkouts:
        checkout_session = stripe.checkout.Session.retrieve(checkout.session_id)
        if checkout_session.payment_status == "completed":

            if not checkout.payment_intent_id:
                checkout.payment_intent_id = checkout_session.payment_intent
                checkout.save()

            if not ItemPaymentTransaction.objects.filter(checkout_session=checkout).exists():
                payment_intent = stripe.PaymentIntent.retrieve(checkout.payment_intent_id)
                handler = PaymentIntentSucceededHandler(payment_intent)
                handler.handle()

        checkout.checkout_status_checked = True
        checkout.save()                


@shared_task
def run_transaction_update():
    """ 
    This tasks ensures that all transactions are up to date
    """
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    transactions = ItemPaymentTransaction.objects.filter(payment_status_checked=False)
    for transaction in transactions:
        payment_intent = stripe.PaymentIntent.retrieve(transaction.payment_intent_id)
        if payment_intent.status != transaction.status:
            if payment_intent.status == ItemPaymentTransaction.statuses.SUCCEEDED:
                handler = PaymentIntentSucceededHandler(payment_intent)
                handler.handle()
            else:
                transaction.status = payment_intent.status
                transaction.save()

        transaction.payment_status_checked = True
        transaction.save()
