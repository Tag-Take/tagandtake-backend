import stripe

from django.http import JsonResponse
from django.conf import settings

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view

from apps.common.responses import create_success_response, create_error_response
from apps.stores.permissions import IsStoreUser
from apps.stores.models import StoreProfile
from apps.supplies.processors import TagsPurchaseProcessor
from apps.stores.models import StoreProfile
from apps.common.responses import create_success_response

stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(["POST"])
def create_member_stipe_account(request: Request):
    try:
        account = stripe.Account.create(
            controller={
                "stripe_dashboard": {
                    "type": "express",
                },
                "fees": {"payer": "application"},
                "losses": {"payments": "application"},
            },
            country="gb",
        )
        return JsonResponse(
            {
                "account": account.id,
            }
        )
    except Exception as e:
        print("An error occurred when calling the Stripe API to create an account: ", e)
        return JsonResponse({"error": str(e)}), 500


@api_view(["POST"])
def create_store_stripe_account(request: Request):
    try:
        account = stripe.Account.create(
            business_type="company",
            controller={
                "stripe_dashboard": {
                    "type": "express",
                },
                "fees": {"payer": "application"},
                "losses": {"payments": "application"},
            },
            country="gb",
        )
        return JsonResponse(
            {
                "account": account.id,
            }
        )
    except Exception as e:
        print("An error occurred when calling the Stripe API to create an account: ", e)
        return JsonResponse({"error": str(e)}), 500


@api_view(["POST"])
def create_stripe_account_session(request: Request):
    try:
        connected_account_id = request.data.get("account")

        account_session = stripe.AccountSession.create(
            account=connected_account_id,
            components={
                "account_onboarding": {"enabled": True},
            },
        )

        return JsonResponse(
            {
                "client_secret": account_session.client_secret,
            }
        )
    except Exception as e:
        print(
            "An error occurred when calling the Stripe API to create an account session: ",
            str(e),
        )
        return JsonResponse({"error": str(e)}), 500


class PurchaseTagsView(APIView):
    permission_classes = [IsAuthenticated, IsStoreUser]

    def get_object(self):
        user = self.request.user
        store_profile = get_object_or_404(StoreProfile, user=user)
        return store_profile

    def post(self, request, *args, **kwargs):
        store_profile = self.get_object()
        group_size = request.data.get("tag_count")

        if group_size is None:
            return create_error_response(
                "Tags count not provided.", {}, status.HTTP_400_BAD_REQUEST
            )

        try:
            group_size = int(group_size)
        except ValueError:
            return create_error_response(
                "Invalid tag count provided.", {}, status.HTTP_400_BAD_REQUEST
            )

        processor = TagsPurchaseProcessor(store_profile.id, group_size)
        processor.process()

        return create_success_response(
            "Tags purchased successfully.", {}, status.HTTP_200_OK
        )
