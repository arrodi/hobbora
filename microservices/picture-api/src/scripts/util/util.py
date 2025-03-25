from scripts.util.imports import *

def generate_filename(user_id, hobby_id=None, picture_id=None):
    # Generates S3 key based on user, hobby, and picture identifiers.
    if hobby_id and picture_id:
        return f"hobby_pictures/{user_id}/{hobby_id}/{picture_id}.webp"
    return f"profile_pictures/{user_id}.webp"

def upload_default_pictures(logger, s3, settings):
    logger.info("Uploading default pictures to S3")

    try:
        s3.client.head_bucket(Bucket=settings.picture_bucket)  # Check if bucket exists
        logger.info(f"Bucket '{settings.picture_bucket}' exists.")
    except Exception as e:
        logger.warning(f"Bucket '{settings.picture_bucket}' does not exist.")
        logger.info(f"Creating bucket: {settings.picture_bucket}")
        s3.create_bucket(settings.picture_bucket)
        logger.info(f"Bucket '{settings.picture_bucket}' created successfully.")

    # Prepare file paths and S3 keys
    files_to_upload = [
        (settings.default_profile_pic_path, generate_filename("default")),
        (settings.default_hobby_pic_path, generate_filename("default", "default", "default_hobby")),
    ]

    # Upload files to S3
    for file_path, s3_key in files_to_upload:
        with open(file_path, "rb") as img_file:
            file_obj = BytesIO(img_file.read())
        try:
            response, status_code = s3.upload_file(file_obj, settings.picture_bucket, s3_key)
            logger.info(f"Uploaded {s3_key} to s3. Response: {response}, Status: {status_code}")
        except Exception as e:
            logger.error(f"Failed to upload {s3_key} to s3. Error: {e}")