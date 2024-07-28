import time
import hashlib
import base64
from io import BytesIO
import qrcode
import uuid

from django.conf import settings
from django.db import transaction

from apps.stores.models import Tag, TagGroup
from apps.common.constants import LISTING
from apps.common.s3.utils import S3ImageHandler
from apps.common.s3.s3_config import FILE_NAMES, get_tag_image_folder, IMAGE_FILE_TYPE


class TagHandler(): 

    # save tag_group, tags and images to s3 atomicly
    def create_tag_group_and_tags(self, store, tag_count):
        tag_hashes = self._create_tag_hashes(tag_count)
        tag_images = self._create_tag_qr_codes(tag_hashes)

        with transaction.atomic():
            tag_group = self.create_tag_group(store, tag_count)
            tags = self.create_tags(tag_group, tag_hashes)

            for i, tag in enumerate(tags):
                folder_namne = get_tag_image_folder(tag_group.id, tag.id)
                key = f"{folder_namne}/{FILE_NAMES['tag']}_{tag.id}_{FILE_NAMES['qr_code']}.{IMAGE_FILE_TYPE}"
                tag_image = tag_images[tag.hash]
                S3ImageHandler().upload_image(tag_image, key)
        

    def create_tag_group(self, store, tag_count):
        tag_group = TagGroup.objects.create(
            store=store,
            group_size=tag_count
        )
        
        return tag_group

    def create_tags(self,tag_group, tag_hashes):
        tags = []
        for i in range(len(tag_hashes)):
            tag = Tag.objects.create(
                tag_group=tag_group,
                hash=tag_hashes[i]
            )
            tags.append(tag)
        
        return tags

    def _create_tag_hashes(self, tag_count):
        tag_hashes = []
        for _ in range(tag_count):
            tag_hashes.append(self._generate_hash())
        
        return tag_hashes

    def _create_tag_qr_codes(self, tag_hashes):
        tag_images = {}
        for tag_hash in tag_hashes:
            tag_images[tag_hash] = self._generate_qr_image(tag_hash)

        return tag_images

    @staticmethod
    def _generate_hash():
        prefix = "tagandbag"
        timestamp = int(time.time() * 1000)  
        unique_uuid = uuid.uuid4() 
        
        # Create a unique string using timestamp and UUID
        unique_str = f"{timestamp}-{unique_uuid}"
        
        # Hash the unique string
        hash_obj = hashlib.sha256(unique_str.encode())
        hashed_component = hash_obj.hexdigest()[:12]  # Using a longer hashed component
        
        # Combine the components to create a raw ID extension
        raw_id_extension = f"{prefix}-{timestamp}-{unique_uuid}-{hashed_component}"
        
        # Encode the raw ID extension in a URL-safe base64 format
        hash = base64.urlsafe_b64encode(raw_id_extension.encode()).decode()
        
        return hash
    
    @staticmethod
    def _generate_qr_image(tag_hash):
        # Generate the QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4) #TODO: refine these values to look good on the tags
        url = f"{settings.FRONTEND_URL}/{LISTING}/{tag_hash}"
        qr.add_data(url)
        qr.make(fit=True)

        # Create QR image
        qr_img = qr.make_image(fill_color="black", back_color="white")

        img_io = BytesIO()
        qr_img.save(img_io, format="PNG")
        img_io.seek(0)

        return img_io
