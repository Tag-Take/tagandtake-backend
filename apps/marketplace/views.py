from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request

from apps.marketplace.serializers import (
    CreateListingSerializer,
    ItemListingSerializer,
    RecallItemListingSerializer,
)
from apps.marketplace.models import ItemListing, RecalledItemListing
from apps.marketplace.utils import (
    get_item_listing_by_tag_id,
    get_item_listing_by_item_id,
)
from apps.marketplace.services.listing_services import (
    ItemListingService,
)
from apps.marketplace.permissions import (
    check_listing_store_permissions,
    check_listing_member_permissions,
)
from apps.items.serializers import ItemCreateSerializer
from apps.items.models import Item
from apps.members.permissions import IsMemberUser
from apps.stores.permissions import IsStoreUser
from apps.common.utils.responses import (
    create_error_response,
    create_success_response,
)
from apps.stores.services.tags_services import TagService
from apps.marketplace.processors import (
    ItemListingCreateProcessor,
    ItemListingRecallProcessor,
    ItemListingDelistProcessor,
    ItemListingCollectProcessor,
    ItemListingReplaceTagProcessor,
    CollectionPinUpdateProcessor,
)
from apps.common.constants import ID, TAG_ID, REASON, NEW_TAG_ID, PIN


class ListingCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = CreateListingSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                listing = serializer.save()
                listing_data = ItemListingSerializer(listing).data
                return create_success_response(
                    "ItemListing created successfully", listing_data, status_code=201
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

    def get_object(self):
        tag = TagService.get_tag(self.request.data.get(TAG_ID))
        return tag

    def create(self, request: Request, *args, **kwargs):
        item_serializer = self.get_serializer(data=request.data)
        if item_serializer.is_valid():
            item: Item = item_serializer.save()
            tag = self.get_object()
            try:
                processor = ItemListingCreateProcessor(item, tag)
                listing = processor.process()
                listing_data = ItemListingSerializer(listing).data
                return create_success_response(
                    "Item and listing created successfully",
                    listing_data,
                    status_code=201,
                )
            except Exception as e:
                return create_error_response(
                    "Error creating listing",
                    {"Exception": str(e)},
                    status.HTTP_400_BAD_REQUEST,
                )
        return create_error_response(
            "Error creating item",
            item_serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )


class ListingRetrieveView(generics.RetrieveAPIView):
    serializer_class = ItemListingSerializer

    def retrieve(self, request: Request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get(ID)
            listing: ItemListing = get_item_listing_by_tag_id(tag_id, ItemListing)
        except serializers.ValidationError as e:
            return create_error_response(e.detail[0], {}, status_code=404)
        try:
            serializer = self.get_serializer(listing)
            role = ItemListingService.get_listing_user_role_from_request(
                request, listing, self
            )
            data = serializer.data | role
            return create_success_response(
                "ItemListing retrieved successfully", data, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error retrieving listing", str(e), status_code=400
            )


class ListingRoleCheckView(generics.RetrieveAPIView):
    def retrieve(self, request: Request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get(ID)
            listing: ItemListing = get_item_listing_by_tag_id(tag_id, ItemListing)
        except serializers.ValidationError as e:
            return create_error_response(e.detail[0], {}, status_code=404)
        try:
            data = ItemListingService.get_listing_user_role_from_request(
                request, listing, self
            )
            return create_success_response(
                "ItemListing role check successful", data, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error checking listing role", str(e), status_code=400
            )


class StoreRecalledListingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]
    serializer_class = RecallItemListingSerializer

    def get_queryset(self):
        try:
            return RecalledItemListing.objects.filter(
                tag__tag_group__store__user=self.request.user
            )
        except serializers.ValidationError as e:
            raise e

    def list(self, request: Request, *args, **kwargs):
        try:
            recalled_listings: list[RecalledItemListing] = self.get_queryset()
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
    serializer_class = ItemListingSerializer

    def update(self, request: Request, *args, **kwargs):
        try:
            item_id = self.kwargs.get(ID)
            listing = get_item_listing_by_item_id(item_id, ItemListing)
        except serializers.ValidationError as e:
            return create_error_response(
                "ItemListing not found", {str(e.detail[0])}, status.HTTP_404_NOT_FOUND
            )

        permission_error_response = check_listing_store_permissions(
            request, self, listing
        )
        if permission_error_response:
            return permission_error_response
        try:
            new_tag = TagService.get_tag(request.data.get(NEW_TAG_ID))
            processor = ItemListingReplaceTagProcessor(listing, new_tag)
            listing = processor.process()
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
    serializer_class = ItemListingSerializer

    def update(self, request: Request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get(ID)
            listing: ItemListing = get_item_listing_by_tag_id(tag_id, ItemListing)
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_store_permissions(
            request, self, listing
        )
        if permission_error_response:
            return permission_error_response

        try:
            reason_id = request.data.get(REASON)
            reason = ItemListingService().get_recall_reasons(reason_id)
            processor = ItemListingRecallProcessor(listing, reason)
            processor.process()
            return create_success_response(
                "ItemListing successfully recalled", {}, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error recalling listing", str(e), status_code=400
            )


class GenerateNewCollectionPinView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request: Request, *args, **kwargs):
        try:
            item_id = self.kwargs.get(ID)
            recalled_listing = get_item_listing_by_item_id(item_id, RecalledItemListing)
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_member_permissions(
            request, self, recalled_listing
        )
        if permission_error_response:
            return permission_error_response
        try:
            processor = CollectionPinUpdateProcessor(recalled_listing)
            processor.process()
            return create_success_response(
                "New collection PIN successfully generated", {}, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error generating new collection PIN", str(e), status_code=400
            )


class DelistListing(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]
    serializer_class = ItemListingSerializer

    def update(self, request: Request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get(ID)
            listing: ItemListing = get_item_listing_by_tag_id(tag_id, ItemListing)
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_store_permissions(
            request, self, listing
        )
        if permission_error_response:
            return permission_error_response

        try:
            reason_id = request.data.get(REASON)
            reason = ItemListingService().get_recall_reasons(reason_id)
            processor = ItemListingDelistProcessor(listing, reason)
            processor.process()
            return create_success_response(
                "ItemListing successfully delisted", {}, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error delisting listing", str(e), status_code=400
            )


class CollectRecalledListingView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ItemListingSerializer

    def update(self, request: Request, *args, **kwargs):
        try:
            item_id = self.kwargs.get(ID)
            recalled_listing: RecalledItemListing = get_item_listing_by_item_id(
                item_id, RecalledItemListing
            )
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_store_permissions(
            request, self, recalled_listing
        )
        if permission_error_response:
            return permission_error_response
        pin = request.data.get(PIN)
        if not pin or not recalled_listing.validate_pin(pin):
            return create_error_response(
                "Invalid PIN.", {PIN: ["Invalid PIN"]}, status.HTTP_400_BAD_REQUEST
            )
        try:
            processor = ItemListingCollectProcessor(recalled_listing)
            processor.process()
            return create_success_response(
                "Recalled listing successfully delisted", {}, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error delisting recalled listing", str(e), status_code=400
            )
