# views/webhooks.py

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from apps.payments.handlers.webhook_handler import handle_stripe_webhook


@csrf_exempt
def stripe_platform_webhook(request):
    """Webhook for platform events."""
    return handle_stripe_webhook(request, settings.STRIPE_PLATFORM_WEBHOOK_SECRET)


@csrf_exempt
def stripe_connect_webhook(request):
    """Webhook for connected account events."""
    return handle_stripe_webhook(request, settings.STRIPE_CONNECT_WEBHOOK_SECRET)
