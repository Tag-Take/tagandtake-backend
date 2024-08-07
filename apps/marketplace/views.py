from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from apps.marketplace.serializers import CreateListingSerializer, ListingSerializer
from apps.marketplace.models import Listing, RecalledListing
from apps.stores.models import Tag
from apps.items.models import Item
from apps.marketplace.services.listing_manager import ListingHandler
from apps.marketplace.permissions import check_listing_store_permissions
from apps.items.serializers import ItemCreateSerializer
from apps.members.permissions import IsMemberUser
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

    def get_object(self):
        tag_id = self.kwargs.get("id")
        try:
            tag = Tag.objects.get(id=tag_id)
            listing = Listing.objects.get(tag=tag)
            return listing
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag not found")
        except Listing.DoesNotExist:
            raise serializers.ValidationError(
                "Listing not found for the provided tag ID"
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except serializers.ValidationError as e:
            return create_error_response(e.detail[0], {}, status_code=404)
        try: 
            serializer = self.get_serializer(instance)
            return create_success_response(
                "Listing retrieved successfully", serializer.data, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error retrieving listing", str(e), status_code=400
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
                    "Item and listing created successfully", listing_data, status_code=201
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

    def get_object(self):
        tag_id = self.kwargs.get("id")
        try:
            tag = Tag.objects.get(id=tag_id)
            listing = Listing.objects.get(tag=tag)
            return listing
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag not found")
        except Listing.DoesNotExist:
            raise serializers.ValidationError(
                "Listing not found for the provided tag ID"
            )
        
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except serializers.ValidationError as e:
            return create_error_response(
                str(e.detail[0]), {}, status_code=404
            )
        permission_error_response = check_listing_store_permissions(request, self, instance)
        if permission_error_response:
            return permission_error_response
        
        reason = request.data.get("reason")
        if reason:
            try:
                ListingHandler(instance).recall_listing(reason)
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

    def get_object(self):
        tag_id = self.kwargs.get("id")
        try:
            tag = Tag.objects.get(id=tag_id)
            listing = Listing.objects.get(tag=tag)
            return listing
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag not found")
        except Listing.DoesNotExist:
            raise serializers.ValidationError(
                "Listing not found for the provided tag ID"
            )
        
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except serializers.ValidationError as e:
            return create_error_response(
                str(e.detail[0]), {}, status_code=404
            )
        permission_error_response = check_listing_store_permissions(request, self, instance)
        if permission_error_response:
            return permission_error_response
        
        reason = request.data.get("reason")
        if reason:
            try:
                ListingHandler(instance).delist_listing(reason)
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

    def get_object(self):
        item_id = self.kwargs.get("id")
        try:
            recalled_listing = RecalledListing.objects.get(item_id=item_id)
            return recalled_listing
        except RecalledListing.DoesNotExist:
            raise serializers.ValidationError(
                "Recalled listing not found for the provided item ID"
            )
        
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
        except serializers.ValidationError as e:
            return create_error_response(
                str(e.detail[0]), {}, status_code=404
            )
        permission_error_response = check_listing_store_permissions(request, self, instance)
        if permission_error_response:
            return permission_error_response
        
        try:
            ListingHandler(instance).delist_recalled_listing()
            return create_success_response(
                "Recalled listing successfully delisted", {}, status_code=200
            )
        except Exception as e:
            return create_error_response(
                "Error delisting recalled listing", str(e), status_code=400
            )

class PurchaseListingView(generics.UpdateAPIView):
    pass