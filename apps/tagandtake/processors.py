from typing import Dict, Any

from django.db import transaction

from apps.common.abstract_classes import AbstractProcessor
from apps.stores.services.tags_services import TagService
from apps.stores.services.store_services import StoreService
from apps.tagandtake.processor_registry import PROCESSOR_REGISTRY   
from apps.common.constants import METADATA, STORE_ID, LINE_ITEMS




class SuppliesPurchaseProcessManager:
    def __init__(self, event_data_obj: Dict[str, Any]):
        self.event_data_obj = event_data_obj
        self.store_id = event_data_obj[METADATA][STORE_ID]
        self.supply_list = event_data_obj[LINE_ITEMS]

    def process_supplies(self):
        for supply in self.supply_list:
            try: 
                processor_class = self._get_processor_class(supply['type'])
                if processor_class: 
                    processor = processor_class()
                    processor.process(supply)
            except Exception as e:
                print(f"Error processing supply {supply['type']}: {e}")

    def _get_processor_class(supply): 
        return PROCESSOR_REGISTRY.get(supply)   


class TagsPurchasedProcessor(AbstractProcessor): 

    def __init__(self, store_id: int, quantity: int): 
        self.store_id = store_id,   
        self.quantity = quantity

    @transaction.atomic
    def process(self):
        store = self._get_store()
        tag_group = self._create_tag_group(store)
        self._generate_tags_for_group(tag_group)
        self._create_and_upload_images(tag_group)

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


