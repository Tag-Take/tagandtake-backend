from django.http import Http404

from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from apps.items.serializers import (
    ItemCreateSerializer,
    ItemRetrieveUpdateDeleteSerializer,
    ItemCategorySerializer,
    ItemConditionSerializer,
)
from apps.members.permissions import IsMemberUser
from apps.items.permissions import IsItemOwner
from apps.items.models import Item, ItemCategory, ItemCondition


class MemberItemListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ItemRetrieveUpdateDeleteSerializer

    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user.member)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ItemCreateSerializer
        return ItemRetrieveUpdateDeleteSerializer


class MemberItemRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsItemOwner]
    serializer_class = ItemRetrieveUpdateDeleteSerializer
    queryset = Item.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound(detail="Item not found")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status != Item.Statuses.AVAILABLE or Item.Statuses.ABANDONED:
            statuses = [
                status
                for status in Item.Statuses
                if status != Item.Statuses.AVAILABLE
                and status != Item.Statuses.ABANDONED
            ]
            joined_statuses = f"{', '.join(statuses[:-1])} or {statuses[-1]}"
            raise ValidationError(
                {
                    "detail": f"This item is currently {instance.status}. Items that are: {joined_statuses} cannot be deleted."
                }
            )

        self.get_serializer(instance).destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemCategoryListView(generics.ListAPIView):
    serializer_class = ItemCategorySerializer
    queryset = ItemCategory.objects.all()


class ItemConditionListView(generics.ListAPIView):
    serializer_class = ItemConditionSerializer
    queryset = ItemCondition.objects.all()
