from rest_framework import permissions
from rest_framework.views import APIView
from apps.marketplace.models import BaseItemListing


class IsTagOwner(permissions.BasePermission):
    def has_object_permission(self, request, view: APIView, listing: BaseItemListing):
        return listing.tag.tag_group.store.user == request.user


class IsListingOwner(permissions.BasePermission):
    def has_object_permission(self, request, view: APIView, listing: BaseItemListing):
        return listing.item.owner_user == request.user
