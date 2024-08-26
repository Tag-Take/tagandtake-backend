

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import serializers

from apps.common.utils.responses import create_success_response, create_error_response
from apps.stores.permissions import IsStoreUser
from apps.stores.models import StoreProfile
from apps.stores.services.tags_services import TagHandler
from apps.stores.models import StoreProfile
from apps.common.utils.responses import create_success_response
from apps.marketplace.utils import get_listing_by_tag_id
from apps.marketplace.services.listing_services import ListingHandler


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
        # TODO: only purchase tags if the store has stripe connect account

        # tags_purchased.send(
        #     sender=StoreProfile, store=store_profile, tag_count=group_size
        # )

        # TODO: Implement this signal correctly ^

        TagHandler(store_profile).create_tag_group_and_tags(group_size)

        return create_success_response(
            "Tags purchased successfully.", {}, status.HTTP_200_OK
        )

class PurchaseListingView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            tag_id = request.data.get("tag_id")
            listing = get_listing_by_tag_id(tag_id)

            ListingHandler.purchase_listing(listing)

            return create_success_response(
                "Listing purchased successfully.", {}, status.HTTP_200_OK
            )

        except serializers.ValidationError as e:
            return create_error_response(
                "Error validating request", {str(e)}, status.HTTP_400_BAD_REQUEST
            )
