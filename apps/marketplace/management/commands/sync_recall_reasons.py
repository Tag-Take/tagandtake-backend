import json
import os

from django.core.management.base import BaseCommand

from apps.marketplace.models import RecallReason


class Command(BaseCommand):
    help = "Sync recall_reasons from fixtures (JSON files)"

    def handle(self, *args, **options):
        base_dir = "apps/marketplace/fixtures"

        # Sync recall reasons
        recall_reasons_file = os.path.join(base_dir, "recall_reasons.json")
        with open(recall_reasons_file, "r") as file:
            recall_reasons = json.load(file)
            self.sync_recall_reasons(recall_reasons)

        self.stdout.write(self.style.SUCCESS("Successfully synced recall reasons"))

    def sync_recall_reasons(self, conditions_data):
        existing_conditions = RecallReason.objects.values_list("reason", flat=True)
        new_conditions = [
            condition["fields"]["reason"] for condition in conditions_data
        ]

        # Add new reason
        for condition in new_conditions:
            if condition not in existing_conditions:
                condition_data = next(
                    c["fields"]
                    for c in conditions_data
                    if c["fields"]["reason"] == condition
                )
                RecallReason.objects.create(
                    reason=condition_data["reason"],
                    type=condition_data["type"],
                    description=condition_data["description"],
                )

        # Remove old reasons
        for condition in existing_conditions:
            if condition not in new_conditions:
                RecallReason.objects.filter(condition=condition).delete()
