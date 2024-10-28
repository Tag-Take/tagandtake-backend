import stripe

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import NotFound

from apps.stores.models import StoreProfile as Store
from apps.payments.services.stripe_services import StripeService
from apps.payments.services.checkout_services import CheckoutSessionService
from apps.payments.services.account_services import PaymentAccountService
from apps.common.constants import *
from .serializers import (
    SessionResponseSerializer,
    AccountStatusSerializer,
    SessionStatusSerializer,
    SuppliesCheckoutSessionSerializer,
)
from apps.marketplace.models import ItemListing
from apps.stores.permissions import IsStoreUser

class PaymentAccountViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        payment_account = PaymentAccountService.get_or_create_payment_account(request.user)
        onboarded = StripeService.is_account_fully_onboarded(payment_account.stripe_account_id)
        serializer = AccountStatusSerializer(data={'onboarded': onboarded})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def onboarding(self, request):
        payment_account = PaymentAccountService.get_or_create_payment_account(request.user)
        session = StripeService.create_stripe_account_onboarding_session(
            payment_account.stripe_account_id
        )
        serializer = SessionResponseSerializer(data={CLIENT_SECRET: session.client_secret})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def management(self, request):
        payment_account = PaymentAccountService.get_or_create_payment_account(request.user)
        session = StripeService.create_stripe_account_management_session(
            payment_account.stripe_account_id
        )
        serializer = SessionResponseSerializer(data={CLIENT_SECRET: session.client_secret})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def payouts(self, request):
        payment_account = PaymentAccountService.get_or_create_payment_account(request.user)
        session = StripeService.create_stripe_account_balances_session(
            payment_account.stripe_account_id
        )
        serializer = SessionResponseSerializer(data={CLIENT_SECRET: session.client_secret})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def payments(self, request):
        payment_account = PaymentAccountService.get_or_create_payment_account(request.user)
        session = StripeService.create_stripe_account_payments_session(
            payment_account.stripe_account_id
        )
        serializer = SessionResponseSerializer(data={CLIENT_SECRET: session.client_secret})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def notifications(self, request):
        payment_account = PaymentAccountService.get_or_create_payment_account(request.user)
        session = StripeService.create_stripe_account_notifications_session(
            payment_account.stripe_account_id
        )
        serializer = SessionResponseSerializer(data={CLIENT_SECRET: session.client_secret})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

class CheckoutViewSet(viewsets.ViewSet):
    def get_item_listing(self, tag_id):
        try:
            return ItemListing.objects.get(tag=tag_id)
        except ItemListing.DoesNotExist:
            raise NotFound(detail=f"No item listing found with tag ID: {tag_id}")

    def get_store(self, user):
        try:
            return Store.objects.get(user=user)
        except Store.DoesNotExist:
            raise NotFound(detail=f"No store found for user: {user.id}")

    @action(detail=False, methods=['post'])
    def item(self, request):
        tag_id = request.data.get(TAG_ID)
        item_listing = self.get_item_listing(tag_id)
        session = StripeService.create_stripe_item_checkout_session(item_listing, tag_id)
        CheckoutSessionService.create_item_checkout_session(session, item_listing)
        
        serializer = SessionResponseSerializer(data={CLIENT_SECRET: session.client_secret})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    @permission_classes([IsStoreUser])
    def supplies(self, request):
        store = self.get_store(request.user)
        serializer = SuppliesCheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        line_items = serializer.save()

        stripe_session = StripeService.create_stripe_supplies_checkout_session(
            line_items, store.id
        )
        CheckoutSessionService.create_supplies_checkout_session(
            stripe_session, store, line_items
        )

        response_serializer = SessionResponseSerializer(
            data={CLIENT_SECRET: stripe_session.client_secret}
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)

    @action(detail=False, methods=['get'], url_path='session-status')
    def session_status(self, request):
        session_id = request.query_params.get(SESSION_ID)
        if not session_id:
            return Response(
                {ERROR: 'No session ID provided.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        session = stripe.checkout.Session.retrieve(session_id)
        serializer = SessionStatusSerializer(data={STATUS: session.status})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)