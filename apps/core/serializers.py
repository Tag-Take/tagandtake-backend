from rest_framework import serializers
from apps.core.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'is_store', 'is_member')

    def validate(self, data):
        """
        Ensure the user is either a store or a member, but not both or neither.
        """
        is_store = data.get('is_store', False)
        is_member = data.get('is_member', False)
        
        if is_store == is_member:
            raise serializers.ValidationError("Each user must be either a store owner or a member. Please select either 'is_store' or 'is_member'.")
        
        return data