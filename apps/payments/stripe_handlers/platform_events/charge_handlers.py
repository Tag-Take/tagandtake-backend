

def handle_charge_succeeded(charge):
    """
    Finalize the transaction when the charge is completed. Ensure metadata from `checkout.session.completed`
    is also present before marking the transaction as "completed".
    """
    transaction = get_or_create_transaction(None, charge['payment_intent'])
    transaction.charge_status = 'succeeded'
    transaction.charge_id = charge['id']
    
    # If payment intent is successful and metadata is available, mark the transaction as completed
    if transaction.payment_status == 'succeeded' and transaction.has_required_metadata():
        transaction.status = 'completed'
    else:
        transaction.status = 'pending'
    
    transaction.save()

