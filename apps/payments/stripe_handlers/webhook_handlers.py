from rest_framework.response import Response
from rest_framework.request import Request
import stripe

from apps.payments.stripe_event_dispatcher import StripeEventDispatcher
from apps.common.constants import TYPE, DATA, OBJECT, ACCOUNT


def handle_stripe_webhook(request: Request, secret: str):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except ValueError:
        return Response(status=400)
    except stripe.error.SignatureVerificationError:
        return Response(status=400)

    event_type = event[TYPE]
    event_data = event[DATA][OBJECT]
    connected_account = event.get(ACCOUNT, None)

    dispatcher = StripeEventDispatcher(event_type, event_data, connected_account)
    dispatcher.dispatch()

    return Response(status=200)
