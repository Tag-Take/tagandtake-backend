from rest_framework import serializers

from apps.tagandtake.models import StoreSupply, SupplyOrderItem


class StoreSupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSupply
        fields = "__all__"


class SupplyOrderItemSerializer(serializers.ModelSerializer):
    supply_id = serializers.PrimaryKeyRelatedField(
        queryset=StoreSupply.objects.all(), source="supply", write_only=True
    )

    class Meta:
        model = SupplyOrderItem
        fields = ["supply_id", "quantity"]
