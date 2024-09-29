from apps.common.constants import TAGS
from apps.supplies.processors import TagsPurchaseProcessor

PROCESSOR_REGISTRY = {
    TAGS: TagsPurchaseProcessor,
}
