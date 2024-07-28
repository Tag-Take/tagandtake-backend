from django.db import transaction
from django.http import Http404

from rest_framework import generics, permissions, status, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from apps.items.serializers import (
    ItemCreateSerializer, 
    ItemRetrieveUpdateDeleteSerializer, 
    MemberItemListSerializer,
    ItemCategorySerializer,
    ItemConditionSerializer,
)
from apps.common.utils.responses import create_error_response, create_success_response
from apps.members.permissions import IsMemberUser
from apps.items.permissions import IsOwner, check_item_permissions
from apps.items.models import Item, ItemCategory, ItemCondition


class ItemCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = ItemCreateSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            item = serializer.save()
            return create_success_response(
                "Item created successfully.",
                {"item": self.get_serializer(item).data},
                status.HTTP_201_CREATED,
            )
        return create_error_response(
            "Item creation failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
        )

class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemRetrieveUpdateDeleteSerializer
    queryset = Item.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            return create_error_response(
                "Item not found.", {}, status.HTTP_404_NOT_FOUND
            )
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if isinstance(instance, Response):  
            return instance
        serializer = self.get_serializer(instance)
        return create_success_response(
            "Item retrieved successfully.",
            {"item": serializer.data},
            status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if isinstance(instance, Response):
            return instance
        permission_response = check_item_permissions(request, self, instance)
        if permission_response:
            return permission_response

        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={"request": request}
        )

        if serializer.is_valid():
            try:
                item = serializer.save()
                return create_success_response(
                    "Item updated successfully.",
                    {"item": serializer.data},
                    status.HTTP_200_OK,
                )
            except serializers.ValidationError as e:
                return create_error_response(
                    "Item update failed.", {"exception": str(e)}, status.HTTP_400_BAD_REQUEST
                )
        return create_error_response(
            "Item update failed.", serializer.errors, status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if isinstance(instance, Response):
            return instance
        permission_response = check_item_permissions(request, self, instance)
        if permission_response:
            return permission_response

        serializer = self.get_serializer(instance)
        try:
            serializer.destroy(instance)
            return create_success_response(
                "Item deleted successfully.", {}, status.HTTP_204_NO_CONTENT
            )
        except serializers.ValidationError as e:
            return create_error_response(
                "Failed to delete item.",
                {"exception": str(e)},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MemberItemListView(generics.ListAPIView):
    serializer_class = MemberItemListSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return create_error_response(
                "No items found for this user.", {}, status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(queryset, many=True)
        return create_success_response(
            "Items retrieved successfully.",
            {"items": serializer.data},
            status.HTTP_200_OK,
        )


class ItemCategoryListView(generics.ListAPIView):
    serializer_class = ItemCategorySerializer
    queryset = ItemCategory.objects.all()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return create_success_response(
            "Item categories retrieved successfully.",
            {"categories": serializer.data},
            status.HTTP_200_OK,
        )


class ItemConditionListView(generics.ListAPIView):
    serializer_class = ItemConditionSerializer
    queryset = ItemCondition.objects.all()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return create_success_response(
            "Item conditions retrieved successfully.",
            {"conditions": serializer.data},
            status.HTTP_200_OK,
        )