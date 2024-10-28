from django.db import transaction

from apps.common.abstract_classes import AbstractProcessor
from apps.stores.services.tags_services import TagService
from apps.stores.models import StoreProfile as Store


class TagsPurchaseProcessor(AbstractProcessor):

    def __init__(self, store: Store, multiplier: int = 1, base_quantity: int = 50):
        self.store = store
        self.quantity = int(base_quantity) * int(multiplier)

    @transaction.atomic
    def process(self):
        tag_group = TagService.create_tag_group(self.store, self.quantity)
        TagService.generate_tags_for_group(tag_group)
        TagService.create_and_upload_tag_group_images(tag_group)
        TagService.send_tag_images_email(tag_group)
