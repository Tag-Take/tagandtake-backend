from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

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

    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user.member)

    def get_serializer_class(self):
        return (
            ItemCreateSerializer
            if self.request.method == "POST"
            else ItemRetrieveUpdateDeleteSerializer
        )


class MemberItemRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsItemOwner]
    serializer_class = ItemRetrieveUpdateDeleteSerializer
    queryset = Item.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.get_serializer(instance).destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemCategoryListView(generics.ListAPIView):
    serializer_class = ItemCategorySerializer
    queryset = ItemCategory.objects.all()


class ItemConditionListView(generics.ListAPIView):
    serializer_class = ItemConditionSerializer
    queryset = ItemCondition.objects.all()
