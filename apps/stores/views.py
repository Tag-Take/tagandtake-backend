from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from apps.stores.models import StoreProfile
from apps.stores.serializers import StoreProfileSerializer


class RetrieveStoreProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StoreProfileSerializer

    def get_object(self):
        user = self.request.user
        if user.is_authenticated and user.role == "store":
            try:
                return StoreProfile.objects.get(user=user)
            except StoreProfile.DoesNotExist:
                raise PermissionDenied("Profile not found.")
        else:
            raise PermissionDenied("You do not have permission to access this profile.")

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile:
            serializer = StoreProfileSerializer(profile)
            return Response(
                {
                    "status": "success",
                    "message": "Profile retrieved successfully.",
                    "data": serializer.data,
                    "errors": {},
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Profile not found or user is not activated.",
                    "data": None,
                    "errors": {},
                },
                status=status.HTTP_403_FORBIDDEN,
            )


# Retrieve Store Profile

# GET /api/v1/stores/profile/
# Update Store Profile (Basic Info)

# PUT /api/v1/stores/profile/basic-info/
# PATCH /api/v1/stores/profile/basic-info/
# Fields: shop_name, phone, store_bio, profile_photo_url
# Update Store Profile (Social Links)

# PUT /api/v1/stores/profile/social-links/
# PATCH /api/v1/stores/profile/social-links/
# Fields: google_profile_url, website_url, instagram_url
# Update Store Profile (Payment Details)

# PUT /api/v1/stores/profile/payment-details/
# PATCH /api/v1/stores/profile/payment-details/
# Fields: stripe_customer_id, stripe_account_id, commission
# Update Store Profile (Store Settings)

# PUT /api/v1/stores/profile/store-settings/
# PATCH /api/v1/stores/profile/store-settings/
# Fields: stock_limit, min_listing_days, min_price
# Update Store Profile (Active Tags Count)

# PUT /api/v1/stores/profile/active-tags-count/
# PATCH /api/v1/stores/profile/active-tags-count/
# Fields: active_tags_count
# Update Store Profile (PIN)

# PUT /api/v1/stores/profile/pin/
# PATCH /api/v1/stores/profile/pin/
# Fields: pin
# Retrieve Store Notification Preferences

# GET /api/v1/stores/profile/notifications/
# Update Store Notification Preferences

# PUT /api/v1/stores/profile/notifications/
# PATCH /api/v1/stores/profile/notifications/
# Retrieve Store Item Categories

# GET /api/v1/stores/profile/item-categories/
# Update Store Item Categories

# POST /api/v1/stores/profile/item-categories/ (Add new category)
# DELETE /api/v1/stores/profile/item-categories/{category_id}/ (Remove category)
# Retrieve Store Item Conditions

# GET /api/v1/stores/profile/item-conditions/
# Update Store Item Conditions

# POST /api/v1/stores/profile/item-conditions/ (Add new condition)
# DELETE /api/v1/stores/profile/item-conditions/{condition_id}/ (Remove condition)
# Retrieve Store Profile Picture

# GET /api/v1/stores/profile/picture/
# Update Store Profile Picture

# PUT /api/v1/stores/profile/picture/
# PATCH /api/v1/stores/profile/picture/
# Delete Store Profile

# DELETE /api/v1/stores/profile/
