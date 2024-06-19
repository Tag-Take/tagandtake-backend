from rest_framework import serializers
from apps.stores.models import StoreProfile

class StoreProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProfile
        fields = "__all__"
