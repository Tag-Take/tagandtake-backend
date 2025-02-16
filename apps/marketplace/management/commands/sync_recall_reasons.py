import json
import os

from django.core.management.base import BaseCommand

from apps.marketplace.models import RecallReason
from apps.common.constants import FIELDS, REASON, TYPE, DESCRIPTION


# TODO: Review and refine recall reasons
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

    def sync_recall_reasons(self, recall_reasons_data: dict):
        existing_reasons = RecallReason.objects.values_list(REASON, flat=True)
        new_reasons = [
            reason[FIELDS][REASON] for reason in recall_reasons_data
        ]

        # Add new reason
        for reason in new_reasons:
            if reason not in existing_reasons:
                reason_data = next(
                    r[FIELDS]
                    for r in recall_reasons_data
                    if r[FIELDS][REASON] == reason
                )
                RecallReason.objects.create(
                    reason=reason_data[REASON],
                    type=reason_data[TYPE],
                    description=reason_data[DESCRIPTION],
                )

        # Remove old reasons
        for reason in existing_reasons:
            if reason not in new_reasons:
                RecallReason.objects.filter(reason=reason).delete()
