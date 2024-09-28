from apps.common.constants import TAGS 
from apps.tagandtake.processors import TagsPurchasedProcessor

PROCESSOR_REGISTRY = {
    TAGS: TagsPurchasedProcessor,
    }
