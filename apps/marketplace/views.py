from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from apps.marketplace.serializers import CreateListingSerializer, ListingSerializer
from apps.marketplace.models import Listing, RecalledListing
from apps.stores.models import Tag
from apps.marketplace.utils import get_listing_by_tag_id, get_listing_by_item_id
from apps.marketplace.services.listing_services import ListingHandler
from apps.marketplace.permissions import check_listing_store_permissions, IsTagOwner
from apps.items.serializers import ItemCreateSerializer
from apps.items.permissions import IsItemOwner
from apps.members.permissions import IsMemberUser
from apps.stores.permissions import IsStoreUser
from apps.common.utils.responses import create_error_response, create_success_response


class ListingCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = CreateListingSerializer

    def create(self, request, *args, **kwargs):
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


class ListingRetrieveView(generics.RetrieveAPIView):
    serializer_class = ListingSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get("id")
            listing = get_listing_by_tag_id(tag_id, Listing)
        except serializers.ValidationError as e:
            return create_error_response(e.detail[0], {}, status_code=404)
        try:
            serializer = self.get_serializer(listing)
            return create_success_response(
                "Listing retrieved successfully", serializer.data, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error retrieving listing", str(e), status_code=400
            )
        

class ListingRoleCheckView(generics.RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get("id")
            listing = get_listing_by_tag_id(tag_id, Listing)
        except serializers.ValidationError as e:
            return create_error_response(e.detail[0], {}, status_code=404)
        try:
            data = {}
            if IsTagOwner().has_object_permission(request, self, listing):
                data["role"] = "HOST_STORE"
            elif IsItemOwner().has_object_permission(request, self, listing.item):
                data["role"] = "ITEM_OWNER"
            elif IsStoreUser().has_permission(request, self):
                data["role"] = "NON_HOST_STORE"
            else:
                data["role"] = "GUEST"
            return create_success_response(
                "Listing role check successful", data, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error checking listing role", str(e), status_code=400
            )


class CreateItemAndListingView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = ItemCreateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                listing = ListingHandler.create_item_and_listing(serializer, request)
                listing_data = ListingSerializer(listing).data
                return create_success_response(
                    "Item and listing created successfully",
                    listing_data,
                    status_code=201,
                )
            except Exception as e:
                return create_error_response(
                    "Error creating item and listing",
                    str(e),
                    status.HTTP_400_BAD_REQUEST,
                )
        return create_error_response(
            "Error creating item and listing",
            serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )


class RecallListingView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListingSerializer

    def update(self, request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get("id")
            listing = get_listing_by_tag_id(tag_id, Listing)
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
                ListingHandler(listing).recall_listing(reason)
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


class DelistListing(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListingSerializer

    def update(self, request, *args, **kwargs):
        try:
            tag_id = self.kwargs.get("id")
            listing = get_listing_by_tag_id(tag_id, Listing)
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
                ListingHandler(listing).delist_listing(reason)
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

    def update(self, request, *args, **kwargs):
        try:
            item_id = self.kwargs.get("id")
            listing = get_listing_by_item_id(item_id, RecalledListing)
        except serializers.ValidationError as e:
            return create_error_response(str(e.detail[0]), {}, status_code=404)
        permission_error_response = check_listing_store_permissions(
            request, self, listing
        )
        if permission_error_response:
            return permission_error_response

        try:
            ListingHandler(listing).delist_recalled_listing()
            return create_success_response(
                "Recalled listing successfully delisted", {}, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error delisting recalled listing", str(e), status_code=400
            )


class PurchaseListingView(generics.UpdateAPIView):
    pass
