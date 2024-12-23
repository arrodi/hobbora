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
        """Uploads a file to the specified S3 bucket."""
        try:
            self.client.upload_fileobj(
                file,
                bucket,
                filename
            )
            return {"message": f"File '{filename}' uploaded successfully to S3!"}, 200
        except ClientError as e:
            logger.error(f"Failed to upload file: {e}", exc_info=True)
            return {"error": "Failed to upload the file."}, 500

    def retrieve_image(self, bucket, key):
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            image_data = response['Body'].read()
            return io.BytesIO(image_data)
        except self.client.exceptions.NoSuchKey:
            logger.warning(f"Image not found in S3: {key}")
            return {"error": "Image not found."}, 404
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to retrieve image: {e}", exc_info=True)
            return {"error": "Image retrieval failed."}, 500
    
    def retrieve_file_paths(self, bucket, prefix):
        file_paths = []
        paginator = self.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                file_paths.append(obj['Key'])

        return file_paths
