from apps.payments.stripe_handlers.platform_events.payment_intent_handlers import (
    PaymentIntentSucceededHandler,
    PaymentIntentFailedHandler
)

PAYMENT_HANDLERS = {
    'payment_intent.succeeded': PaymentIntentSucceededHandler,
    'payment_intent.failed': PaymentIntentFailedHandler,
    }

STRIPE_HANDLER_REGISTRY = {
    'platform': {
        **PAYMENT_HANDLERS,
    }
}
