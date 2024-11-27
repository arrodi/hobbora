from os import environ
import os

class Settings:
    def __init__(self):
        self.s3_host=environ["S3_ENDPOINT"]
        self.s3_user=environ["S3_USER"]
        self.s3_password=environ["S3_PASS"]
        
        self.app_host=environ["APP_HOST"]
        self.app_port=environ["APP_PORT"]

        self.picture_bucket=environ["PICTURE_BUCKET"]
        self.default_pic_path=environ["DEFAULT_PIC_PATH"]