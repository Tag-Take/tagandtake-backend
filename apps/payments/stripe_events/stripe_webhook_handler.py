from rest_framework.response import Response
from rest_framework.request import Request
import stripe

from apps.payments.stripe_events.stripe_event_dispatcher import StripeEventDispatcher
from apps.common.constants import TYPE, DATA, OBJECT, ACCOUNT


def route_stripe_webhook(request: Request, secret: str):
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

    if event_type == "capability.updated" or event_type == "account.updated":
        print(event_data)

    dispatcher = StripeEventDispatcher(event_type, event_data, connected_account)
    dispatcher.dispatch()

    return Response(status=200)
