from PIL import Image, ImageFont, ImageDraw
import qrcode
from io import BytesIO
import zipfile

from django.conf import settings
from django.db import transaction

from rest_framework import serializers

from apps.stores.models import Tag, TagGroup, StoreProfile
from apps.common.constants import LISTING
from apps.common.s3.s3_utils import S3Service
from apps.common.s3.s3_config import get_tag_image_key
from apps.common.constants import LISTING
from apps.notifications.emails.services.email_senders import OperationsEmailSender


class TagService:
    @staticmethod
    def get_tag(tag_id: int):
        try:
            return Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag does not exist.")

    @staticmethod
    def create_tag(tag_group: TagGroup):
        tag = Tag.objects.create(tag_group=tag_group)
        return tag

    @staticmethod
    def create_tag_group(store: StoreProfile, group_size: int):
        tag_group = TagGroup.objects.create(store=store, group_size=group_size)
        return tag_group

    @transaction.atomic
    @staticmethod
    def generate_tags_for_group(tag_group: TagGroup):
        Tag.objects.filter(tag_group=tag_group).delete()
        tags = [TagService.create_tag(tag_group) for _ in range(tag_group.group_size)]
        return tags

    @staticmethod
    def upload_tag_image(tag: Tag, tag_image):
        key = get_tag_image_key(tag)
        S3Service().upload_image(tag_image, key)

    @staticmethod
    def get_listing_url(tag: Tag):
        return f"{settings.FRONTEND_URL}/{LISTING}/{tag.id}"

    @staticmethod
    def generate_tag_image(url: str, tag_id: int):
        # Generate QR code
        qr = qrcode.QRCode(version=2, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        
        img_width, img_height = qr_img.size
        total_height = img_height + 30  # Extra space below the QR code for the tag ID

        new_img = Image.new("RGB", (img_width, total_height), "white")
        new_img.paste(qr_img, (0, 0))

        draw = ImageDraw.Draw(new_img)
        tag_text = 'TAG: '+str(tag_id)

        font_size = 24
        font = ImageFont.truetype(settings.TAG_FONT, font_size)  

        # Calculate text position
        bbox = draw.textbbox((0, 0), tag_text, font=font) 
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x_position = (img_width - text_width) // 2
        y_position = total_height - text_height - 32

        # Draw the text using the Nunito-Bold font
        draw.text((x_position, y_position), tag_text, fill="black", align="center", font=font)    

        # Save the image to a BytesIO object
        img_io = BytesIO()
        new_img.save(img_io, format="PNG")
        img_io.seek(0)

        return img_io


    @staticmethod
    def create_and_upload_tag_group_images(tag_group: TagGroup):
        tags = tag_group.tags.all()
        for tag in tags:
            listing_url = TagService.get_listing_url(tag)
            tag_image = TagService.generate_tag_image(listing_url, tag.id)
            TagService.upload_tag_image(tag, tag_image)

    @staticmethod
    def generate_tag_group_images_zipfile(tag_group):
        tags = tag_group.tags.all()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for tag in tags:
                listing_url = TagService.get_listing_url(tag)
                tag_image = TagService.generate_tag_image(listing_url, tag.id)
                filename = f"tag_{tag.id}.png"
                zip_file.writestr(filename, tag_image.read())
        zip_buffer.seek(0)
        return zip_buffer

    @staticmethod
    def send_tag_images_email(tag_group):
        zip_file = TagService.generate_tag_group_images_zipfile(tag_group)

        attachment = (
            f"tag_images_{tag_group.id}.zip",
            zip_file.read(),
            "application/zip",
        )

        OperationsEmailSender.send_tag_images_email(tag_group, attachment)
