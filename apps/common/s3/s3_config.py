from apps.common.constants import *

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


def get_member_profile_folder(instance_id: int):
    return f"{BASE_PATHS[MEMBERS]}/{BASE_PATHS[PROFILES]}/{instance_id}"


def get_store_profile_folder(instance_id: int):
    return f"{BASE_PATHS[STORES]}/{BASE_PATHS[PROFILES]}/{instance_id}"


def get_item_images_folder(item_id: int):
    return f"{BASE_PATHS[ITEMS]}/{item_id}/{BASE_PATHS[IMAGES]}"


def get_tag_image_folder(tag_group_id: int, tag_id: int):
    return f"{BASE_PATHS[TAGS]}/{BASE_PATHS[GROUPS]}/{tag_group_id}/{tag_id}"
