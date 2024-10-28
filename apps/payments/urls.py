from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentAccountViewSet, CheckoutViewSet
from .webhooks import stripe_connect_event_webhook, stripe_platform_event_webhook

router = DefaultRouter()

router.register(r'payment-accounts', PaymentAccountViewSet, basename='payment-account')
router.register(r'checkout', CheckoutViewSet, basename='checkout')

urlpatterns = [
    path('', include(router.urls)),
    path(
        "stripe/platform-webhook/",
        stripe_platform_event_webhook,
        name="stripe-platform-webhook",
    ),
    path(
        "stripe/connect-webhook/",
        stripe_connect_event_webhook,
        name="stripe-connect-webhook",
    ),
]
