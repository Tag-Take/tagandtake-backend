import json
import os

from django.core.management.base import BaseCommand
from apps.payments.models.providers import PaymentProvider, PayoutProvider


class Command(BaseCommand):
    help = "Sync payment and payout providers from fixtures (JSON files)"

    def handle(self, *args, **options):
        base_dir = "apps/payments/fixtures"

        payment_providers_file = os.path.join(base_dir, "payment_providers.json")
        if os.path.exists(payment_providers_file):
            with open(payment_providers_file, "r") as file:
                payment_providers = json.load(file)
                self.sync_providers(payment_providers, PaymentProvider)
        else:
            self.stdout.write(self.style.WARNING("Payment providers file not found."))

        payout_providers_file = os.path.join(base_dir, "payout_providers.json")
        if os.path.exists(payout_providers_file):
            with open(payout_providers_file, "r") as file:
                payout_providers = json.load(file)
                self.sync_providers(payout_providers, PayoutProvider)
        else:
            self.stdout.write(self.style.WARNING("Payout providers file not found."))

        self.stdout.write(
            self.style.SUCCESS("Successfully synced payment and payout providers")
        )

    def sync_providers(self, providers_data, model_class):
        existing_providers = model_class.objects.values_list("name", flat=True)
        new_providers = [provider["fields"]["name"] for provider in providers_data]

        for provider_name in new_providers:
            if provider_name not in existing_providers:
                provider_data = next(
                    p["fields"]
                    for p in providers_data
                    if p["fields"]["name"] == provider_name
                )
                model_class.objects.create(
                    name=provider_data["name"],
                    description=provider_data["description"],
                    api_url=provider_data["api_url"],
                )

        for provider_name in existing_providers:
            if provider_name not in new_providers:
                model_class.objects.filter(name=provider_name).delete()
