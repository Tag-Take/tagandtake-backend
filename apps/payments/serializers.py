from rest_framework import serializers

from apps.tagandtake.models import StoreSupply
from apps.tagandtake.serializers import SupplyOrderItemSerializer


class SuppliesCheckoutSessionSerializer(serializers.Serializer):
    supplies = SupplyOrderItemSerializer(many=True)

    def validate(self, data):
        supplies = data.get("supplies", [])

        for supply in supplies:
            supply_obj = supply["supply"]
            if not supply_obj.stripe_price_id:
                raise serializers.ValidationError(
                    f"Supply ID {supply_obj.id} is missing Stripe price ID."
                )

        return data

    def create(self, validated_data):
        supply_data = validated_data["supplies"]

        line_items = []
        for supply in supply_data:
            supply_obj = supply["supply"]
            line_items.append(
                {
                    "price": supply_obj.stripe_price_id,
                    "quantity": supply["quantity"],
                }
            )
        return line_items
