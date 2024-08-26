from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request

from apps.marketplace.serializers import (
    CreateListingSerializer,
    ListingSerializer,
    RecallListingSerializer,
)
from apps.marketplace.models import Listing, RecalledListing
from apps.marketplace.utils import (
    get_listing_by_tag_id,
    get_listing_by_item_id,
)
from apps.marketplace.services.listing_services import (
    ListingHandler,
    get_listing_user_role,
)
from apps.marketplace.permissions import check_listing_store_permissions
from apps.items.serializers import ItemCreateSerializer
from apps.items.models import Item
from apps.members.permissions import IsMemberUser
from apps.stores.permissions import IsStoreUser
from apps.common.utils.responses import (
    create_error_response,
    create_success_response,
    extract_error_messages,
)


class ListingCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = CreateListingSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                listing = serializer.save()
                listing_data = ListingSerializer(listing).data
                return create_success_response(
                    "Listing created successfully", listing_data, status_code=201
                )
            except Exception as e:
                return create_error_response(
                    "Error creating listing", str(e), status_code=400
                )
        return create_error_response(
            "Error creating listing", serializer.errors, status_code=400
        )


class CreateItemAndListingView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = ItemCreateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request: Request, *args, **kwargs):
        item_serializer = self.get_serializer(data=request.data)
        if item_serializer.is_valid():
            item: Item = item_serializer.save()
            tag_id = request.data.get("tag_id")
            try:
                listing = ListingHandler().create_listing(
                    item_id=item.id, tag_id=tag_id
                )
                listing_data = ListingSerializer(listing).data
                return create_success_response(
                    "Item and listing created successfully",
                    listing_data,
                    status_code=201,
                )
            except Exception as e:
                return create_error_response(
                    "Error creating listing",
                    extract_error_messages(e),
                    status.HTTP_400_BAD_REQUEST,
                )
        return create_error_response(
            "Error creating item",
            item_serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )


class ListingRetrieveView(generics.RetrieveAPIView):
    serializer_class = ListingSerializer

    def retrieve(self, request: Request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get("id")
            listing: Listing = get_listing_by_tag_id(tag_id, Listing)
        except serializers.ValidationError as e:
            return create_error_response(e.detail[0], {}, status_code=404)
        try:
            serializer = self.get_serializer(listing)
            role = get_listing_user_role(request, listing, self)
            data = serializer.data | role
            return create_success_response(
                "Listing retrieved successfully", data, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error retrieving listing", str(e), status_code=400
            )


class ListingRoleCheckView(generics.RetrieveAPIView):
    def retrieve(self, request: Request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get("id")
            listing: Listing = get_listing_by_tag_id(tag_id, Listing)
        except serializers.ValidationError as e:
            return create_error_response(e.detail[0], {}, status_code=404)
        try:
            data = get_listing_user_role(request, listing, self)
            return create_success_response(
                "Listing role check successful", data, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error checking listing role", str(e), status_code=400
            )


class StoreRecalledListingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]
    serializer_class = RecallListingSerializer

    def get_queryset(self):
        try:
            return RecalledListing.objects.filter(
                tag__tag_group__store__user=self.request.user
            )
        except serializers.ValidationError as e:
            raise e

    def list(self, request: Request, *args, **kwargs):
        try:
            recalled_listings: list[RecalledListing] = self.get_queryset()
            if not recalled_listings.exists():
                return create_error_response(
                    "No RecalledListings found.", {}, status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(recalled_listings, many=True)
            return create_success_response(
                "Recalled listings retrieved successfully",
                {"recalled_listings": serializer.data},
                status_code=200,
            )
        except serializers.ValidationError as e:
            return create_error_response(e.detail[0], {}, status_code=404)
        except Exception as e:
            return create_error_response(
                "Error retrieving recalled listings", str(e), status_code=400
            )


class ReplaceTagView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListingSerializer

    def update(self, request: Request, *args, **kwargs):
        item_id = self.kwargs.get("id")

        try:
            listing = get_listing_by_item_id(item_id, Listing)
        except serializers.ValidationError as e:
            return create_error_response(
                "Listing not found", {str(e.detail[0])}, status.HTTP_404_NOT_FOUND
            )

        permission_error_response = check_listing_store_permissions(
            request, self, listing
        )
        if permission_error_response:
            return permission_error_response

        new_tag_id = request.data.get("new_tag_id")
        if not new_tag_id:
            return create_error_response(
                "new_tag_id is required to update listing.",
                {},
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            listing = ListingHandler().replace_listing_tag(listing, new_tag_id)
            serializer = self.get_serializer(listing)
            return create_success_response(
                "Tag successfully replaced.", serializer.data, status.HTTP_200_OK
            )
        except serializers.ValidationError as e:
            return create_error_response(
                str(e.detail[0]), {}, status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return create_error_response(
                "Error replacing tag", str(e), status.HTTP_400_BAD_REQUEST
            )


class RecallListingView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListingSerializer

    def update(self, request: Request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get("id")
            listing: Listing = get_listing_by_tag_id(tag_id, Listing)
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_store_permissions(
            request, self, listing
        )
        if permission_error_response:
            return permission_error_response

        reason = request.data.get("reason")
        if reason:
            try:
                ListingHandler().recall_listing(listing, reason)
                return create_success_response(
                    "Listing successfully recalled", {}, status_code=200
                )
            except Exception as e:
                return create_error_response(
                    "Error recalling listing", str(e), status_code=400
                )
        return create_error_response(
            "Reason is required to recall a listing", {}, status_code=400
        )
    

class GenerateNewCollectionPinView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request: Request, *args, **kwargs):
        try:
            item_id = self.kwargs.get("id")
            recalled_listing: Listing = get_listing_by_item_id(item_id, RecalledListing)
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_store_permissions(
            request, self, recalled_listing
        )
        if permission_error_response:
            return permission_error_response
        try:
            ListingHandler().generate_new_collection_pin(recalled_listing)
            return create_success_response(
                "New collection PIN successfully generated", {}, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error generating new collection PIN", str(e), status_code=400
            )

class DelistListing(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListingSerializer

    def update(self, request: Request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get("id")
            listing: Listing = get_listing_by_tag_id(tag_id, Listing)
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_store_permissions(
            request, self, listing
        )
        if permission_error_response:
            return permission_error_response

        reason = request.data.get("reason")
        if reason:
            try:
                ListingHandler().delist_listing(listing, reason)
                return create_success_response(
                    "Listing successfully delisted", {}, status_code=200
                )
            except Exception as e:
                return create_error_response(
                    "Error delisting listing", str(e), status_code=400
                )
        return create_error_response(
            "Reason is required to delist a listing", {}, status_code=400
        )


class DelistRecalledListingView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListingSerializer

    def update(self, request: Request, *args, **kwargs):
        try:
            item_id = self.kwargs.get("id")
            recalled_listing: RecalledListing = get_listing_by_item_id(
                item_id, RecalledListing
            )
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_store_permissions(
            request, self, recalled_listing
        )
        if permission_error_response:
            return permission_error_response

        try:
            ListingHandler.delist_recalled_listing(recalled_listing)
            return create_success_response(
                "Recalled listing successfully delisted", {}, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error delisting recalled listing", str(e), status_code=400
            )
