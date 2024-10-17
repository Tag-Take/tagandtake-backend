from django.db import transaction

from apps.common.abstract_classes import AbstractProcessor
from apps.stores.services.tags_services import TagService
from apps.stores.services.store_services import StoreService
from apps.stores.models import StoreProfile as Store


class TagsPurchaseProcessor(AbstractProcessor):

    def __init__(self, store: Store, multiplier: int = 1, base_quantity: int = 50):
        self.store = store
        self.quantity = int(base_quantity) * int(multiplier)

    @transaction.atomic
    def process(self):
        tag_group = self._create_tag_group()
        self._generate_tags_for_group(tag_group)
        self._create_and_upload_images(tag_group)
        self._send_tag_images_email(tag_group)

    def _get_store(self):
        store = StoreService.get_store(self.store.id)
        return store

    def _create_tag_group(self):
        tag_group = TagService.create_tag_group(self.store, self.quantity)
        return tag_group

    def _generate_tags_for_group(self, tag_group):
        TagService.generate_tags_for_group(tag_group)

    def _create_and_upload_images(self, tag_group):
        TagService.create_and_upload_tag_group_images(tag_group)

    @staticmethod
    def _send_tag_images_email(tag_group):
        TagService.send_tag_images_email(tag_group)
