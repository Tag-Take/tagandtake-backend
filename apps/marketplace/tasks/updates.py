from celery import shared_task
from django.utils.timezone import now
from apps.marketplace.models import RecalledItemListing
from apps.marketplace.processors import ItemListingAbandonedProcessor


@shared_task
def run_abandoned_item_updates():
    recalled_listings = RecalledItemListing.objects.filter(
        collection_deadline__lt=now()
    )
    for listing in recalled_listings:
        run_task_for_listing.delay(listing.id)


@shared_task
def run_task_for_listing(recalled_listing_id):
    recalled_listing = RecalledItemListing.objects.get(id=recalled_listing_id)
    handler = ItemListingAbandonedProcessor(recalled_listing)
    handler.process()
