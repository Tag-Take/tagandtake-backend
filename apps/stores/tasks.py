from django.db import transaction

from celery import shared_task

from apps.stores.models import StoreProfile
from apps.stores.services.tags_services import TagService


@shared_task
def create_tags_task(store_id: int, group_size: int):
    store = StoreProfile.objects.get(id=store_id)

    with transaction.atomic():
        tag_group = TagService.create_tag_group(store, group_size)
        TagService.generate_tags_for_group(tag_group)
        TagService.create_and_upload_tag_group_images(tag_group)
