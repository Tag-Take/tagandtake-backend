from rest_framework.response import Response
from rest_framework.request import Request
import stripe

from apps.payments.stripe_event_dispatcher import StripeEventDispatcher


def handle_stripe_webhook(request: Request, secret: str):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except ValueError:
        return Response(status=400)
    except stripe.error.SignatureVerificationError:
        return Response(status=400)

    event_type = event["type"]
    event_data = event["data"]["object"]
    connected_account = event.get("account", None)

    dispatcher = StripeEventDispatcher(event_type, event_data, connected_account)
    dispatcher.dispatch()

    return Response(status=200)
