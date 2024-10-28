from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentAccountViewSet, CheckoutViewSet
from .webhooks import stripe_connect_event_webhook, stripe_platform_event_webhook

# Initialize the router
router = DefaultRouter()

# Register viewsets
router.register(r'payment-accounts', PaymentAccountViewSet, basename='payment-account')
router.register(r'checkout', CheckoutViewSet, basename='checkout')

# Define URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Webhook endpoints
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
