from typing import Dict, Any

from django.db import transaction

from apps.common.abstract_classes import AbstractProcessor
from apps.stores.services.tags_services import TagService
from apps.stores.services.store_services import StoreService
from apps.supplies.services import SuppliesServices
from apps.payments.services.transaction_services import TransactionService
from apps.supplies.processor_registry import PROCESSOR_REGISTRY
from apps.common.constants import METADATA, STORE_ID, LINE_ITEMS, PRICE


class SuppliesPurchaseProcessManager:
    def __init__(self, event_data_obj: Dict[str, Any]):
        self.event_data_obj = event_data_obj
        self.store_id = event_data_obj[METADATA][STORE_ID]
        self.supplies_list = event_data_obj[LINE_ITEMS]

    @transaction.atomic
    def process_supplies(self):
        transaction = self._create_supplies_transaction()
        self._create_supplies_order_items(transaction)

        for supply in self.supplies_list:
            processor_class = self._get_processor_class(supply[PRICE])
            if processor_class:
                processor = processor_class()
                processor.process(self.store_id, supply)

        self._send_confirmation_email()
        self._notify_us()

    def _create_supplies_transaction(self):
        return TransactionService().upsert_supplies_transaction(self.event_data_obj)

    def _create_supplies_order_items(self, transaction):
        SuppliesServices.create_supplies_order_items(
            transaction, self.store_id, self.supplies_list
        )

    def _get_processor_class(supply):
        return PROCESSOR_REGISTRY.get(supply)

    def _send_confirmation_email(self):
        # TODO
        pass

    def _notify_us(self):
        # TODO
        pass


class TagsPurchaseProcessor(AbstractProcessor):

    def __init__(self, store_id: int, quantity: int):
        self.store_id = store_id
        self.quantity = quantity

    @transaction.atomic
    def process(self):
        store = self._get_store()
        tag_group = self._create_tag_group(store)
        self._generate_tags_for_group(tag_group)
        self._create_and_upload_images(tag_group)
        self._notify_us()

    def _get_store(self):
        store = StoreService.get_store(self.store_id)
        return store

    def _create_tag_group(self, store):
        tag_group = TagService.create_tag_group(store, self.quantity)
        return tag_group

    def _generate_tags_for_group(self, tag_group):
        TagService.generate_tags_for_group(tag_group)

    def _create_and_upload_images(self, tag_group):
        TagService.create_and_upload_tag_group_images(tag_group)

    def _notify_us(self):
        # TODO
        pass
