import json
import os

from django.core.management.base import BaseCommand

from apps.items.models import ItemCategory, ItemCondition
from apps.common.constants import FIELDS, CONDITION, NAME, DESCRIPTION


class Command(BaseCommand):
    help = "Sync item categories and conditions from fixtures (JSON files)"

    def handle(self, *args, **options):
        base_dir = "apps/items/fixtures"

        # Sync conditions
        conditions_file = os.path.join(base_dir, "item_conditions.json")
        with open(conditions_file, "r") as file:
            conditions_data = json.load(file)
            self.sync_conditions(conditions_data)

        # Sync categories
        categories_file = os.path.join(base_dir, "item_categories.json")
        with open(categories_file, "r") as file:
            categories_data = json.load(file)
            self.sync_categories(categories_data)

        self.stdout.write(
            self.style.SUCCESS("Successfully synced item categories and conditions")
        )

    def sync_conditions(self, conditions_data: dict):
        existing_conditions = ItemCondition.objects.values_list(CONDITION, flat=True)
        new_conditions = [condition[FIELDS][CONDITION] for condition in conditions_data]

        # Add new conditions
        for condition in new_conditions:
            if condition not in existing_conditions:
                condition_data = next(
                    c[FIELDS]
                    for c in conditions_data
                    if c[FIELDS][CONDITION] == condition
                )
                ItemCondition.objects.create(
                    condition=condition_data[CONDITION],
                    description=condition_data[DESCRIPTION],
                )

        # Remove old conditions
        for condition in existing_conditions:
            if condition not in new_conditions:
                ItemCondition.objects.filter(condition=condition).delete()

    def sync_categories(self, categories_data: dict):
        existing_categories = ItemCategory.objects.values_list(NAME, flat=True)
        new_categories = [category[FIELDS][NAME] for category in categories_data]

        # Add new categories
        for category in new_categories:
            if category not in existing_categories:
                category_data = next(
                    c[FIELDS] for c in categories_data if c[FIELDS][NAME] == category
                )
                ItemCategory.objects.create(
                    name=category_data[NAME], description=category_data[DESCRIPTION]
                )

        # Remove old categories
        for category in existing_categories:
            if category not in new_categories:
                ItemCategory.objects.filter(name=category).delete()
