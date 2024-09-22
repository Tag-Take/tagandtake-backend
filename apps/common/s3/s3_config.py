from apps.common.constants import *
from apps.members.models import MemberProfile as Member
from apps.stores.models import StoreProfile as Store, Tag
from apps.items.models import Item

PRSIGNED_URL_EXPIRATION: int = 3600
BASE_PATHS = {
    MEMBERS: MEMBERS,
    STORES: STORES,
    ITEMS: ITEMS,
    IMAGES: IMAGES,
    PROFILES: PROFILES,
    TAGS: TAGS,
    GROUPS: GROUPS,
}
IMAGE_FILE_TYPE = "jpg"
FILE_NAMES = {
    "profile_photo": "profile_photo",
    "item_image": "item_image",
    "tag": "tag",
    "qr_code": "qr_code",
}


def get_member_profile_photo_key(member: Member):
    return f"{MEMBERS}/{member.id}/{PROFILE_PHOTO}/{PROFILE}.{IMAGE_FILE_TYPE}"


def get_store_profile_photo_key(store: Store):
    return f"{STORES}/{store.id}/{PROFILE_PHOTO}/{PROFILE}.{IMAGE_FILE_TYPE}"


def get_item_image_key(item: Item, order=0):
    return f"{MEMBERS}/{item.owner.id}/{ITEMS}/{item.id}/{ITEM_IMAGE}_{order}.{IMAGE_FILE_TYPE}"


def get_tag_image_key(tag: Tag):
    return f"{STORES}/{tag.store.id}/{TAG_GROUPS}/{tag.tag_group}/{IMAGES}/{TAG}_{tag.id}_{QR_CODE}.{IMAGE_FILE_TYPE}"
