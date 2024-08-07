import boto3
from celery import shared_task
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from django.conf import settings
from tempfile import NamedTemporaryFile
import os



class S3BaseHandler:
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

    def generate_s3_url(self, key):
        return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}"

    def generate_presigned_url(self, key, expiration=3600):
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

class S3ImageHandler(S3BaseHandler):

    def upload_image(self, file, key):
        with NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.read())
            tmp_file_path = tmp_file.name
        return upload_image_task.delay(tmp_file_path, key)

    def delete_image(self, key):
        return delete_image_task.delay(key)

@shared_task
def upload_image_task(file_path, key):
    s3_client = boto3.client('s3')
    try:
        with open(file_path, 'rb') as file:
            s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, key)
        os.remove(file_path)  # Clean up the temporary file
        return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}"
    except ClientError as e:
        raise Exception(f"Failed to upload file to S3: {e}") from e
    except Exception as e:
        raise Exception(f"Error uploading file to S3: {e}") from e

@shared_task
def delete_image_task(key):
    s3_client = boto3.client('s3')
    try:
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
    except ClientError as e:
        raise Exception(f"Failed to delete file from S3: {e}") from e
    except Exception as e:
        raise Exception(f"Error deleting file from S3: {e}") from e
