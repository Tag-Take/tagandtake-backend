# from apps.payments.utils import get_or_create_item_transaction, get_or_create_supply_transaction

# def handle_payment_intent_succeeded(payment_intent):
#     """
#     Handle the successful payment intent but wait for charge confirmation and metadata from
#     `checkout.session.completed`.
#     """

#     transaction = get_or_create_transaction(None, payment_intent["id"])
#     transaction.payment_status = "succeeded"

#     # If charge is already succeeded and metadata is available, complete the transaction
#     if transaction.charge_status == "succeeded" and transaction.has_required_metadata():
#         transaction.status = "completed"
#     else:
#         transaction.status = "pending"
#     TODO: transfer funds based on latest_charge in payment_intent

#     transaction.save()


# def handle_payment_intent_failed(payment_intent):
#     """
#     If the payment intent failed, mark the transaction as failed.
#     """
#     transaction = get_or_create_transaction(None, payment_intent["id"])
#     transaction.status = "failed"
#     transaction.save()
