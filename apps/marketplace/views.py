
from rest_framework import generics, permissions
from rest_framework import serializers

from apps.marketplace.serializers import CreateListingSerializer, ListingSerializer
from apps.marketplace.models import Listing, Item, Tag
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
                return create_success_response(
                    "Listing created successfully", serializer.data, status_code=201
                )
            except Exception as e:
                return create_error_response(
                    "Error creating listing", str(e), status_code=400
                )
        return create_error_response(
            "Error creating listing", serializer.errors, status_code=400
        )

# view to retrieve listing by hash
class ListingRetrieveView(generics.RetrieveAPIView):
    serializer_class = ListingSerializer

    def get_object(self):
        tag_id = self.kwargs.get('id')
        try:
            tag = Tag.objects.get(id=tag_id)
            listing = Listing.objects.get(tag=tag)
            return listing
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag not found")
        except Listing.DoesNotExist:
            raise serializers.ValidationError("Listing not found for the provided tag ID")

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return create_success_response(
                "Listing retrieved successfully", serializer.data, status_code=200
            )
        except serializers.ValidationError as e:
            return create_error_response(
                e.detail[0], {}, status_code=404
            )