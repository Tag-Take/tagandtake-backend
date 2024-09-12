from rest_framework.decorators import api_view
from rest_framework.response import Response
import stripe

from apps.tag.models import StoreSupply


@api_view(["POST"])
def create_store_supply_checkout_session(request, supply_id):
    """Creates a Stripe Checkout session for a store supply."""
    supply = StoreSupply.objects.get(id=supply_id)
    store = request.user.storeprofile  # Assuming the user is linked to a store profile

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": supply.stripe_price_id,  # Use Stripe Price ID
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri("/success/"),
            cancel_url=request.build_absolute_uri("/cancel/"),
            metadata={
                "supply_id": supply.id,
                "store_id": store.id,  # Save the store making the purchase
            },
        )
        return Response({"sessionId": session.id})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
