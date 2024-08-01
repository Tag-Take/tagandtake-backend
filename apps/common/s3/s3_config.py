# Define the base paths for different entities
BASE_PATHS = {
    "members": "members",
    "stores": "stores",
    "items": "items",
    "images": "images",
    "profiles": "profiles",
    "tags": "tags",
    "groups": "groups",
}

IMAGE_FILE_TYPE = "jpg"

FILE_NAMES = {
    "profile_photo": "profile_photo",
    "item_image": "item_image",
    "tag": "tag",
    "qr_code": "qr_code",
}


def get_member_profile_folder(instance_id):
    return f"{BASE_PATHS['members']}/{BASE_PATHS['profiles']}/{instance_id}"


def get_store_profile_folder(instance_id):
    return f"{BASE_PATHS['stores']}/{BASE_PATHS['profiles']}/{instance_id}"


def get_item_images_folder(item_id):
    return f"{BASE_PATHS['items']}/{item_id}/{BASE_PATHS['images']}"


def get_tag_image_folder(tag_group_id, tag_id):
    return f"{BASE_PATHS['tags']}/{BASE_PATHS['groups']}/{tag_group_id}/{tag_id}"
