from django.utils.timezone import now
from decimal import Decimal
from apps.marketplace.models import RecalledListing
from apps.marketplace.services.listing_manager import ListingHandler


class StorageFeeService:
    def __init__(self, recalled_listing: RecalledListing):
        self.recalled_listing = recalled_listing

    def is_time_to_charge(self):
        return now() >= self.recalled_listing.next_fee_charge_at

    def apply_storage_fee(self):
        if self.is_time_to_charge():
            # TODO: apply charge to the user's account
            ListingHandler(self.recalled_listing).apply_recurring_storage_fee()

    @staticmethod
    def run_storage_fee_checks():
        recalled_listings = RecalledListing.objects.all()
        for recalled_listing in recalled_listings:
            service = StorageFeeService(recalled_listing)
            if service.is_time_to_charge():
                service.apply_storage_fee() 

