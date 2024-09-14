from rest_framework import serializers

from apps.tagandtake.models import StoreSupply
from apps.tagandtake.serializers import SupplyOrderItemSerializer


class SuppliesCheckoutSessionSerializer(serializers.Serializer):
    items = SupplyOrderItemSerializer(many=True)  # Use the nested serializer for items

    def validate_items(self, value):
        for item in value:
            try:
                supply = StoreSupply.objects.get(id=item["supply_id"])
                if not supply.stripe_price_id:
                    raise serializers.ValidationError(
                        f"Supply ID {item['supply_id']} is missing Stripe price ID."
                    )
            except StoreSupply.DoesNotExist:
                raise serializers.ValidationError(
                    f"Supply ID {item['supply_id']} not found."
                )
        return value

    def create(self, validated_data):
        items_data = validated_data["items"]

        line_items = []
        for item in items_data:
            supply = StoreSupply.objects.get(
                id=item["supply_id"]
            )  # Fetch the supply details
            line_items.append(
                {
                    "price": supply.stripe_price_id,
                    "quantity": item["quantity"],
                }
            )

        return line_items
