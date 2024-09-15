from apps.payments.models.transactions import ItemPaymentTransaction, SupplyPaymentTransaction

def get_or_create_item_transaction(session_id=None, payment_intent_id=None):
    """
    Either create a new transaction or update an existing one based on session or payment intent ID.
    """
    if session_id:
        transaction, created = ItemPaymentTransaction.objects.get_or_create(session_id=session_id)
    elif payment_intent_id:
        transaction, created = ItemPaymentTransaction.objects.get_or_create(payment_intent_id=payment_intent_id)
    else:
        raise ValueError("Either session_id or payment_intent_id must be provided.")
    
    return transaction

def get_or_create_supply_transaction(session_id=None, payment_intent_id=None):
    """
    Either create a new transaction or update an existing one based on session or payment intent ID.
    """
    if session_id:
        transaction, created = SupplyPaymentTransaction.objects.get_or_create(session_id=session_id)
    elif payment_intent_id:
        transaction, created = SupplyPaymentTransaction.objects.get_or_create(payment_intent_id=payment_intent_id)
    else:
        raise ValueError("Either session_id or payment_intent_id must be provided.")
    
    return transaction