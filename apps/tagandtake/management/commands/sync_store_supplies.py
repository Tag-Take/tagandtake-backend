import json
import os

from django.core.management.base import BaseCommand
from apps.tagandtake.models import StoreSupply


class Command(BaseCommand):
    help = "Sync store supplies from fixtures (JSON files)"

    def handle(self, *args, **options):
        base_dir = "apps/tagandtake/fixtures"

        # Sync store supplies
        store_supplies_file = os.path.join(base_dir, "store_supplies.json")
        with open(store_supplies_file, "r") as file:
            store_supplies = json.load(file)
            self.sync_store_supplies(store_supplies)

        self.stdout.write(self.style.SUCCESS("Successfully synced store supplies"))

    def sync_store_supplies(self, store_supplies_data: dict):
        existing_supplies = StoreSupply.objects.values_list("name", flat=True)
        new_supplies = [supply["fields"]["name"] for supply in store_supplies_data]

        # Add new supplies
        for supply_name in new_supplies:
            if supply_name not in existing_supplies:
                supply_data = next(
                    s["fields"]
                    for s in store_supplies_data
                    if s["fields"]["name"] == supply_name
                )
                StoreSupply.objects.create(
                    name=supply_data["name"],
                    description=supply_data["description"],
                    stripe_price_id=supply_data["stripe_price_id"],
                    price=supply_data["price"],
                )

        # Remove old supplies
        for supply_name in existing_supplies:
            if supply_name not in new_supplies:
                StoreSupply.objects.filter(name=supply_name).delete()
