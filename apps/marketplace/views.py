from rest_framework import generics, permissions, serializers, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from apps.marketplace.serializers import (
    CreateListingSerializer,
    CreateItemAndListingSerializer,
    ItemListingSerializer,
    RecallItemListingSerializer,
)
from apps.items.serializers import FlatItemSerializer
from apps.marketplace.models import ItemListing, RecalledItemListing
from apps.marketplace.services.listing_services import (
    ItemListingService,
)
from apps.marketplace.permissions import IsTagOwner, IsListingOwner
from apps.members.permissions import IsMemberUser
from apps.stores.permissions import IsStoreUser
from apps.marketplace.models import RecallReason
from apps.stores.models import Tag
from apps.marketplace.services.listing_services import ItemListingService
from apps.stores.services.tags_services import TagService
from apps.marketplace.processors import (
    ItemListingRecallProcessor,
    ItemListingDelistProcessor,
    ItemListingCollectProcessor,
    ItemListingReplaceTagProcessor,
    CollectionPinUpdateProcessor,
)
from apps.common.constants import *


class ListingCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = CreateListingSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = serializer.save()
        listing_data = ItemListingSerializer(listing, context={REQUEST: request}).data
        return Response({MESSAGE: "Listing successfully created.", DATA: listing_data}, status=status.HTTP_201_CREATED)


class CreateItemAndListingView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = CreateItemAndListingSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request: Request, *args, **kwargs):
        item_fields = FlatItemSerializer.Meta.fields
        item_data = {field: request.data.get(field) for field in request.data if field in item_fields}
        preprocessed_data = {
            TAG_ID: request.data.get(TAG_ID),
            ITEM: item_data 
        }
        serializer = self.get_serializer(data=preprocessed_data, context={REQUEST: request})
        serializer.is_valid(raise_exception=True)
        listing = serializer.save()
        listing_data = ItemListingSerializer(listing, context={REQUEST: request}).data 
        return Response({MESSAGE: "Listing successfully created.", DATA: listing_data}, status=status.HTTP_201_CREATED)


class ListingRetrieveView(generics.RetrieveAPIView):
    serializer_class = ItemListingSerializer

    def get_object(self):
        tag_id = self.kwargs.get(ID)
        listing = ItemListing.objects.filter(tag__id=tag_id).first()
        if listing:
            return listing
        else: 
            try:
                return Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                raise NotFound({DETAIL: "Tag does not exist."})

class ListingRoleCheckView(APIView):
    def get(self, request, *args, **kwargs):
        tag_id = self.kwargs.get(ID)
        try:
            tag = TagService.get_tag(tag_id)
            listing = ItemListing.objects.filter(tag__id=tag_id).first()
            
            if listing:
                user_relation = ItemListingService.get_user_listing_relation(request, listing)
                listing_exists = True
            else:
                user_relation = TagService.get_user_tag_relation(request, tag)
                listing_exists = False
            
            response_data = {
                USER_LISTING_RELATION: user_relation,
                LISTING_EXISTS: listing_exists
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            raise NotFound(detail=str(e.detail[0]))

class StoreRecalledListingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]
    serializer_class = RecallItemListingSerializer

    def get_queryset(self):
        return RecalledItemListing.objects.filter(
            tag__tag_group__store__user=self.request.user
        )


class StoreItemListingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStoreUser]
    serializer_class = ItemListingSerializer

    def get_queryset(self):
        return RecalledItemListing.objects.filter(
            tag__tag_group__store__user=self.request.user
        )


class ReplaceTagView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTagOwner]
    serializer_class = ItemListingSerializer

    def get_object(self):
        item_id = self.kwargs.get("id")
        try:
            listing = ItemListing.objects.get(item__id=item_id)
            self.check_object_permissions(self.request, listing)
            return listing
        except ItemListing.DoesNotExist:
            raise NotFound(detail=f"ItemListing not found for the provided item ID: {item_id}")

    def update(self, request: Request, *args, **kwargs):
        instance = self.get_object()

        try:
            new_tag = TagService.get_tag(request.data.get(NEW_TAG_ID))
        except Tag.DoesNotExist:
            raise NotFound(detail="The new tag does not exist.")

        processor = ItemListingReplaceTagProcessor(instance, new_tag)
        listing = processor.process()

        serializer = self.get_serializer(listing, context={REQUEST: request})
        return Response({MESSAGE: "Tag successfully replaced.", DATA: serializer.data}, status=status.HTTP_200_OK)


class RecallListingView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTagOwner]
    serializer_class = RecallItemListingSerializer

    def get_object(self):
        tag_id = self.kwargs.get(ID)
        try:
            listing = ItemListing.objects.get(tag__id=tag_id)
            self.check_object_permissions(self.request, listing)
            return listing
        except ItemListing.DoesNotExist:
            raise NotFound(detail=f"ItemListing not found for the provided tag ID: {tag_id}")

    def update(self, request: Request, *args, **kwargs):
        listing = self.get_object()
        reason_id = request.data.get(REASON)

        try:
            reason = RecallReason.objects.get(id=reason_id)
        except Exception as e:
            return Response({DETAIL: str(e)}, status=status.HTTP_400_BAD_REQUEST)

        processor = ItemListingRecallProcessor(listing, reason)
        recalled_listing = processor.process()

        serializer = self.get_serializer(recalled_listing, context={REQUEST: request})
        return Response({
            MESSAGE: "ItemListing successfully recalled",
            DATA: serializer.data
        }, status=status.HTTP_200_OK)


class GenerateNewCollectionPinView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsListingOwner]
    serializer_class = RecallItemListingSerializer

    def get_object(self):
        item_id = self.kwargs.get(ID)
        try:
            recalled_listing = RecalledItemListing.objects.get(item__id=item_id)
            self.check_object_permissions(self.request, recalled_listing)
            return recalled_listing
        except serializers.ValidationError as e:
            raise NotFound(detail=str(e.detail[0]))

    def update(self, request: Request, *args, **kwargs):
        recalled_listing = self.get_object()
        
        processor = CollectionPinUpdateProcessor(recalled_listing)
        updated_listing = processor.process()
        
        serializer = self.get_serializer(updated_listing, context={REQUEST: request})
        return Response({
            MESSAGE: "New collection PIN successfully generated",
            DATA: serializer.data
        }, status=status.HTTP_200_OK)


class DelistListing(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTagOwner]
    serializer_class = RecallItemListingSerializer

    def get_object(self):
        tag_id = self.kwargs.get(ID)
        try:
            listing = ItemListing.objects.get(tag__id=tag_id)
            self.check_object_permissions(self.request, listing)
            return listing
        except ItemListing.DoesNotExist:
            raise NotFound(detail=f"ItemListing not found for the provided item ID: {item_id}")

    def update(self, request: Request, *args, **kwargs):
        listing = self.get_object()
        reason_id = request.data.get(REASON)

        try:
            reason = ItemListingService().get_recall_reasons(reason_id)
        except Exception as e:
            return Response({DETAIL: str(e)}, status=status.HTTP_400_BAD_REQUEST)

        processor = ItemListingDelistProcessor(listing, reason)
        recalled_listing = processor.process()

        serializer = self.get_serializer(recalled_listing, context={REQUEST: request})
        return Response({
            MESSAGE: "ItemListing successfully delisted",
            DATA: serializer.data
        }, status=status.HTTP_200_OK)


class CollectRecalledListingView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsTagOwner]
    serializer_class = RecallItemListingSerializer

    def get_object(self):
        item_id = self.kwargs.get(ID)
        try:
            listing = RecalledItemListing.objects.get(item__id=item_id)
            self.check_object_permissions(self.request, listing)
            return listing
        except serializers.ValidationError as e:
            raise NotFound(detail=str(e.detail[0]))

    def update(self, request: Request, *args, **kwargs):
        recalled_listing = self.get_object()
        pin = request.data.get(PIN)

        if not pin or not recalled_listing.validate_pin(pin):
            return Response({DETAIL: "Invalid PIN."}, status=status.HTTP_400_BAD_REQUEST)

        processor = ItemListingCollectProcessor(recalled_listing)
        collected_listing = processor.process()

        serializer = self.get_serializer(collected_listing, context={REQUEST: request})
        return Response({
            MESSAGE: "Recalled listing successfully collected",
            DATA: serializer.data
        }, status=status.HTTP_200_OK)
