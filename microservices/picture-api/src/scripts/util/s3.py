# STL IMPORTS
import logging
import io

# EXT IMPORTS
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3:
    def __init__(self, access_key, secret_key, endpoint):
        logger.info("Initializing S3 client...")
        logger.info(f"Access Key: {access_key} Endpoint: {endpoint}")
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                endpoint_url=endpoint,
                verify=False
            )
            logger.info("S3 client initialized successfully.")
        except BotoCoreError as e:
            logger.error(f"Failed to initialize S3 client: {e}", exc_info=True)
            raise

    def upload_file(self, file, bucket, filename):
        try:
            self.client.upload_fileobj(
                file,
                bucket,
                filename
            )
            return True, "Uploaded file"
        except self.client.exceptions.NoSuchBucket as e:
            logger.error(f"Failed to upload file: {e}", exc_info=True)
            return False , "NoSuchBucket"
        except ClientError as e:
            logger.error(f"Failed to upload file: {e}", exc_info=True)
            return False , "Failed to upload file"
        
    
    def delete_file(self, bucket, filename):
        try:
            self.client.delete_object(Bucket=bucket, Key=filename)
            logger.info(f"File '{filename}' deleted successfully from bucket '{bucket}'.")
            return True, "Deleted successfully"
        except self.client.exceptions.NoSuchKey:
            logger.warning(f"File not found in S3: {filename}")
            return False, "File not found in S3: {filename}"
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to delete file: {e}", exc_info=True)
            return False, "Failed to delete file"

    def retrieve_image(self, bucket, key):
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            image_data = response['Body'].read()
            return True, io.BytesIO(image_data), "Image Found"
        except self.client.exceptions.NoSuchKey:
            logger.warning(f"Image not found in S3: {key}")
            return True, b"", "Image not found."
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to retrieve image: {e}", exc_info=True)
            return False, b"", "Image retrieval failed."
    
    def retrieve_file_paths(self, bucket, prefix):
        file_paths = []
        paginator = self.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                file_paths.append(obj['Key'])

        return file_paths
    
    def create_bucket(self, bucket_name):
        try:
            self.client.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' created successfully.")
            return True, "Bucket created successfully."
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to create bucket: {e}", exc_info=True)
            return False, "Failed to create bucket."
