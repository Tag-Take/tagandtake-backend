import json
import os

from django.core.management.base import BaseCommand
from apps.supplies.models import StoreSupply
from apps.common.constants import NAME, FIELDS, STRIPE_PRICE_ID, PRICE, DESCRIPTION


class Command(BaseCommand):
    help = "Sync store supplies from fixtures (JSON files)"

    def handle(self, *args, **options):
        base_dir = "apps/supplies/fixtures"

        # Sync store supplies
        store_supplies_file = os.path.join(base_dir, "store_supplies.json")
        with open(store_supplies_file, "r") as file:
            store_supplies = json.load(file)
            self.sync_store_supplies(store_supplies)

        self.stdout.write(self.style.SUCCESS("Successfully synced store supplies"))


    def sync_store_supplies(self, store_supplies_data: dict):
        existing_supplies = StoreSupply.objects.values_list(NAME, flat=True)
        new_supplies = [supply[FIELDS][NAME] for supply in store_supplies_data]

        for supply in store_supplies_data:
            supply_data = supply[FIELDS]
            supply_name = supply_data[NAME]

            if supply_name in existing_supplies:
                StoreSupply.objects.filter(name=supply_name).update(
                    description=supply_data[DESCRIPTION],
                    stripe_price_id=supply_data[STRIPE_PRICE_ID],
                    price=supply_data[PRICE],
                )
            else:
                StoreSupply.objects.create(
                    name=supply_data[NAME],
                    description=supply_data[DESCRIPTION],
                    stripe_price_id=supply_data[STRIPE_PRICE_ID],
                    price=supply_data[PRICE],
                )

        for supply_name in existing_supplies:
            if supply_name not in new_supplies:
                StoreSupply.objects.filter(name=supply_name).delete()

