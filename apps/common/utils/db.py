from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

def create_instance_with_related_models(model_class, instance_data, related_data):
    """
    Creates an instance of the specified model_class and related models in a transactional manner.

    Args:
        model_class: The main model class to create an instance of.
        instance_data: Dictionary containing data for the main model instance.
        related_data: Dictionary where the keys are the related model classes, and the values are dictionaries containing:
                      - foreign_key_name: The name of the foreign key field on the related model.
                      - data: The data for creating instances of the related model (can be a list for multiple instances).

    Returns:
        instance: The created main model instance.
    """
    instances = {}
    
    try:
        with transaction.atomic():
            # Step 1: Create the main instance (e.g., User)
            if model_class == User:
                instances[model_class] = model_class.objects.create_user(
                    username=instance_data.get("username"),
                    email=instance_data.get("email"),
                    password=instance_data.get("password"),
                    role=instance_data.get("role")
                )
            else:
                instances[model_class] = model_class.objects.create(**instance_data)

            # Step 2: Create the related instances using the appropriate foreign key reference
            for related_model_class, related_info in related_data.items():
                foreign_key_name = related_info['foreign_key_name']
                related_instances_data = related_info['data']

                # Ensure the related instances are created with the correct foreign key reference to the relevant instance
                if not isinstance(related_instances_data, list):
                    related_instances_data = [related_instances_data]

                for related_data_item in related_instances_data:
                    # Use the appropriate instance for the foreign key reference
                    foreign_key_instance = instances[related_info['related_model']]

                    related_instance = related_model_class.objects.create(**{foreign_key_name: foreign_key_instance, **related_data_item})
                    instances[related_model_class] = related_instance

            return instances[model_class]

    except Exception as e:
        raise serializers.ValidationError(
            {f"{model_class.__name__.lower()}_creation_error": f"Error creating {model_class.__name__.lower()} and related models: {str(e)}"}
        )
