from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from apps.payments.stripe_handlers.webhook_handlers import handle_stripe_webhook


@csrf_exempt
@api_view(["POST"])
def stripe_platform_event_webhook(request):
    return handle_stripe_webhook(request, settings.STRIPE_PLATFORM_WEBHOOK_SECRET)


@csrf_exempt
@api_view(["POST"])
def stripe_connect_event_webhook(request):
    return handle_stripe_webhook(request, settings.STRIPE_CONNECT_WEBHOOK_SECRET)