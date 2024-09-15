from apps.payments.utils import get_or_create_item_transaction, get_or_create_supply_transaction

# Example handler functions
def handle_checkout_session_completed(session):
    """Handle Stripe's checkout.session.completed event."""
    metadata = session['metadata']
    if metadata.get('product') == 'item':
        transaction = get_or_create_item_transaction(session['id'], session['payment_intent'])
    elif metadata.get('product') == 'supply':
        transaction = get_or_create_supply_transaction(session['id'], session['payment_intent'])

    metadata.pop('product')

    for key, value in metadata.items():
        setattr(transaction, key, value)

    if transaction.payment_status == 'succeeded' and transaction.charge_status == 'succeeded':
        transaction.status = 'completed'
    else:
        transaction.status = 'pending'
    
    transaction.save()


def handle_checkout_session_expired(session):
    """Handle Stripe's checkout.session.expired event."""
    pass


