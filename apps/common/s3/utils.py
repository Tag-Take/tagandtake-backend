import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from django.conf import settings

def get_s3_client():
    try:
        return boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise Exception("AWS credentials error") from e
    except Exception as e:
        raise Exception("Error creating S3 client") from e

def create_folder_in_s3(folder_name):
    s3 = get_s3_client()
    try:
        s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f"{folder_name}/")
    except ClientError as e:
        raise Exception("Failed to create folder in S3") from e
    except Exception as e:
        raise Exception("Error creating folder in S3") from e

def upload_file_to_s3(file, key):
    s3 = get_s3_client()
    try:
        s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, key)
    except ClientError as e:
        raise Exception("Failed to upload file to S3") from e
    except Exception as e:
        raise Exception("Error uploading file to S3") from e

def generate_s3_url(key):
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{key}"

def generate_store_profile_folder_name(instance_id):
    return f'stores/profiles/{instance_id}'

def generate_member_profile_folder_name(instance_id):
    return f'members/profiles/{instance_id}'

### Generate pre-signed URL for Testing
def generate_presigned_url(key, expiration=3600):
    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        raise Exception("Failed to generate pre-signed URL") from e
    except Exception as e:
        raise Exception("Error generating pre-signed URL") from e

