from django.db import transaction
from apps.items.models import ItemCategory, ItemCondition
from apps.stores.models import StoreItemCategorie, StoreItemConditions

@transaction.atomic
def create_store_item_categories_and_conditions(store_profile):
    # TODO: Add filtering to set default categories and conditions
    item_categories = ItemCategory.objects.all()
    item_conditions = ItemCondition.objects.all()

    for category in item_categories:
        StoreItemCategorie.objects.create(store=store_profile, category=category)

    for condition in item_conditions:
        StoreItemConditions.objects.create(store=store_profile, condition=condition)