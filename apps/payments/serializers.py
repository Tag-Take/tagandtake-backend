from rest_framework import serializers

from apps.supplies.models import StoreSupply
from apps.supplies.serializers import SupplyOrderItemSerializer
from apps.common.constants import SUPPLIES, SUPPLY, QUANTITY, PRICE


class SuppliesCheckoutSessionSerializer(serializers.Serializer):
    supplies = SupplyOrderItemSerializer(many=True)

    def validate(self, data):
        supplies = data.get(SUPPLIES, [])

        for supply in supplies:
            supply_obj = supply[SUPPLY]
            supply = StoreSupply.objects.filter(
                stripe_price_id=supply_obj.stripe_price_id
            ).first()
            if not supply:
                raise serializers.ValidationError("Supply does not exist.")

        return data

    def create(self, validated_data):
        supply_data = validated_data[SUPPLIES]

        line_items = []
        for supply in supply_data:
            supply_obj = supply[SUPPLY]
            line_items.append(
                {
                    PRICE: supply_obj.stripe_price_id,
                    QUANTITY: supply[QUANTITY],
                }
            )
        return line_items
