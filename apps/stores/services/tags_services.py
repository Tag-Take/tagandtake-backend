import qrcode
from io import BytesIO

from django.conf import settings
from django.db import transaction

from rest_framework import serializers

from apps.stores.models import Tag, TagGroup, StoreProfile
from apps.common.constants import LISTING
from apps.common.s3.s3_utils import S3ImageHandler
from apps.common.s3.s3_config import FILE_NAMES, get_tag_image_folder, IMAGE_FILE_TYPE
from apps.common.constants import LISTING, TAG, QR_CODE


class TagService:
    @staticmethod
    def get_tag(tag_id: int):
        try:
            return Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag does not exist.")
    
    @staticmethod
    def create_tag_group(store: StoreProfile, group_size: int):
        tag_group = TagGroup.objects.create(
            store=store, group_size=group_size
        )
        return tag_group

    @staticmethod
    def create_tag(tag_group: TagGroup):
        tag = Tag.objects.create(tag_group=tag_group)
        return tag

    @transaction.atomic
    @staticmethod
    def generate_tags_for_group(tag_group: TagGroup):
        Tag.objects.filter(tag_group=tag_group).delete()
        tags = [
            TagService.create_tag(tag_group)
            for _ in range(tag_group.group_size)
        ]
        return tags

    @staticmethod
    def create_and_upload_tag_group_images(tag_group: TagGroup):
        tags = tag_group.tags.all()
        for tag in tags:
            tag_image = TagService.generate_tag_image(tag)
            TagService.upload_tag_image(tag, tag_image)

    @staticmethod
    def upload_tag_image(tag: Tag, tag_image):
        folder_namne = get_tag_image_folder(tag.tag_group.id, tag.id)
        key = f"{folder_namne}/{FILE_NAMES[TAG]}_{tag.id}_{FILE_NAMES[QR_CODE]}.{IMAGE_FILE_TYPE}"
        S3ImageHandler().upload_image(tag_image, key)

    @staticmethod
    def generate_tag_image(tag: Tag):
        qr: qrcode = qrcode.QRCode(version=1, box_size=10, border=4)
        url = f"{settings.FRONTEND_URL}/{LISTING}/{tag.id}"
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        img_io = BytesIO()
        qr_img.save(img_io, format="PNG")
        img_io.seek(0)
        return img_io
