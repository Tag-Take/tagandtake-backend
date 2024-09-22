from io import BytesIO
import qrcode

from django.conf import settings
from django.db import transaction

from rest_framework import serializers

from apps.stores.models import Tag, TagGroup
from apps.common.constants import LISTING
from apps.common.s3.s3_utils import S3ImageHandler
from apps.common.s3.s3_config import FILE_NAMES, get_tag_image_folder, IMAGE_FILE_TYPE
from apps.common.constants import LISTING, TAG, QR_CODE
from apps.common.abstract_classes import AbstractHandler
from apps.stores.models import StoreProfile

class TagService:
    @staticmethod
    def get_tag(tag_id: int):
        try:
            return Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag does not exist.")


class CreateTagsHandler(AbstractHandler):
    def __init__(self, store: StoreProfile, group_size: int) -> None:
        self.store = store
        self.group_size = group_size

    @transaction.atomic
    def handle(self):
        tag_group = self.create_tag_group()
        tags = self.create_tags(tag_group)
        self.generate_tag_images(tags, tag_group)

    def create_tag_group(self):
        tag_group = TagGroup.objects.create(store=self.store, group_size=self.group_size)
        return tag_group

    @staticmethod
    def create_tags(tag_group: TagGroup):
        tags = []
        for i in range(tag_group.group_size):
            tag = Tag.objects.create(tag_group=tag_group)
            tags.append(tag)
        return tags

    def generate_tag_images(self, tags, tag_group):
        for i, tag in enumerate(tags):
            folder_namne = get_tag_image_folder(tag_group.id, tag.id)
            key = f"{folder_namne}/{FILE_NAMES[TAG]}_{tag.id}_{FILE_NAMES[QR_CODE]}.{IMAGE_FILE_TYPE}"
            tag_image = self._generate_qr_image(tag.id)
            S3ImageHandler().upload_image(tag_image, key)

    @staticmethod
    def _generate_qr_image(tag_id):
        qr: qrcode = qrcode.QRCode(version=1, box_size=10, border=4)
        url = f"{settings.FRONTEND_URL}/{LISTING}/{tag_id}"
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        img_io = BytesIO()
        qr_img.save(img_io, format="PNG")
        img_io.seek(0)
        return img_io
