from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404

from apps.common.utils.responses import create_success_response, create_error_response

from apps.stores.permissions import IsStoreUser
from apps.stores.models import StoreProfile

from apps.payments.signals import tags_purchased
from apps.stores.models import StoreProfile
from apps.common.utils.responses import create_success_response


# create dummy view for now to send signal to create tag group and tags for a store (to be handled elsewhere)

class PurchaseTagsView(APIView):
    permission_classes = [IsAuthenticated, IsStoreUser]

    def get_object(self):
        # Assumes user is authenticated and the user object is available
        user = self.request.user
        store_profile = get_object_or_404(StoreProfile, user=user)
        return store_profile

    def post(self, request, *args, **kwargs):
        store_profile = self.get_object()
        group_size = request.data.get("tag_count")

        if group_size is None:
            return create_error_response(
                "Tags count not provided.", {}, status.HTTP_400_BAD_REQUEST
            )

        try:
            group_size = int(group_size)
        except ValueError:
            return create_error_response(
                "Invalid tag count provided.", {}, status.HTTP_400_BAD_REQUEST
            )

        tags_purchased.send(sender=StoreProfile, store=store_profile, tag_count=group_size)

        return create_success_response(
            "Tags purchased successfully.", {}, status.HTTP_200_OK
        )

