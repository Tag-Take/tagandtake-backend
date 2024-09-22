from typing import BinaryIO

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from django.conf import settings
from apps.common.s3.s3_config import PRSIGNED_URL_EXPIRATION


class S3ClientBase:
    def __init__(self):
        self.s3_client = self.get_s3_client()

    def get_s3_client(self):
        try:
            return boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise Exception(f"AWS credentials error: {e}") from e
        except Exception as e:
            raise Exception(f"Error creating S3 client: {e}") from e

    def generate_s3_url(self, key: str):
        return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}"


class S3Service(S3ClientBase):
    def upload_image(self, file: BinaryIO, key: str):
        try:
            self.s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, key)
            return self.generate_s3_url(key)
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {e}") from e
        except Exception as e:
            raise Exception(f"Error uploading file to S3: {e}") from e

    def delete_image(self, key: str):
        try:
            self.s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key
            )
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3: {e}") from e
        except Exception as e:
            raise Exception(f"Error deleting file from S3: {e}") from e

    def generate_presigned_url(
        self, key: str, expiration: int = PRSIGNED_URL_EXPIRATION
    ):
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate pre-signed URL: {e}") from e
        except Exception as e:
            raise Exception(f"Error generating pre-signed URL: {e}") from e
