from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from apps.items.serializers import ItemCreateSerializer
from apps.common.utils.responses import create_error_response, create_success_response
from apps.members.permissions import IsMemberUser


class ItemCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsMemberUser]
    serializer_class = ItemCreateSerializer
    parser_classes = (MultiPartParser, FormParser)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            return create_success_response(
                "Item created successfully.",
                {"item": self.get_serializer(item).data},
                status.HTTP_201_CREATED
            )
        return create_error_response(
            "Item creation failed.",
            serializer.errors,
            status.HTTP_400_BAD_REQUEST
        )


# Get all items from a user
# GET /api/items/member/<int:user_id>/

# Get a single item
# GET /api/items/<int:item_id>/

# Update an item
# PUT /api/items/<int:item_id>/

# Delete an item
# DELETE /api/items/<int:item_id>/

# Get all item categories
# GET /api/items/categories/

# Get all item conditions
# GET /api/items/conditions/
