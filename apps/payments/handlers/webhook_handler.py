from django.conf import settings
from django.http import HttpResponse

from rest_framework import request

import stripe

from apps.payments.stripe_event_dispatcher import StripeEventDispatcher


def handle_stripe_webhook(request: request, secret: str):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event["type"]
    event_data = event["data"]["object"]

    connected_account = event.get("account", None)

    dispatcher = StripeEventDispatcher(event_type, event_data, connected_account)
    dispatcher.dispatch()

    return HttpResponse(status=200)
