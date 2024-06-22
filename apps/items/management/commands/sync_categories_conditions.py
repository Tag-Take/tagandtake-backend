import json
import os

from django.core.management.base import BaseCommand
from django.apps import apps

from apps.items.models import ItemCategory, ItemCondition


class Command(BaseCommand):
    help = 'Sync item categories and conditions from fixtures (JSON files)'

    def handle(self, *args, **options):
        # Get the app config to determine the correct fixture directory
        app_config = apps.get_app_config('apps.items')
        base_dir = os.path.join(app_config.path, 'fixtures')

        # Sync conditions
        conditions_file = os.path.join(base_dir, 'item_conditions.json')
        with open(conditions_file, 'r') as file:
            conditions_data = json.load(file)
            self.sync_conditions(conditions_data)
        
        # Sync categories
        categories_file = os.path.join(base_dir, 'item_categories.json')
        with open(categories_file, 'r') as file:
            categories_data = json.load(file)
            self.sync_categories(categories_data)
        
        self.stdout.write(self.style.SUCCESS('Successfully synced item categories and conditions'))

    def sync_conditions(self, conditions_data):
        existing_conditions = ItemCondition.objects.values_list('condition', flat=True)
        new_conditions = [condition['condition'] for condition in conditions_data]
        
        # Add new conditions
        for condition in new_conditions:
            if condition not in existing_conditions:
                ItemCondition.objects.create(
                    condition=condition,
                    description=[c['description'] for c in conditions_data if c['condition'] == condition][0]
                )
        
        # Remove old conditions
        for condition in existing_conditions:
            if condition not in new_conditions:
                ItemCondition.objects.filter(condition=condition).delete()

    def sync_categories(self, categories_data):
        existing_categories = ItemCategory.objects.values_list('name', flat=True)
        new_categories = [category['name'] for category in categories_data]
        
        # Add new categories
        for category in new_categories:
            if category not in existing_categories:
                ItemCategory.objects.create(
                    name=category,
                    description=[c['description'] for c in categories_data if c['name'] == category][0]
                )
        
        # Remove old categories
        for category in existing_categories:
            if category not in new_categories:
                ItemCategory.objects.filter(name=category).delete()
