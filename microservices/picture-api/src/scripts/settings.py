from os import environ

print("te3t")

class Settings:
    def __init__(self):
        self.s3_host=environ["S3_ENDPOINT"]
        self.s3_user=environ["S3_USER"]
        self.s3_password=environ["S3_PASS"]
        
        self.app_host=environ["APP_HOST"]
        self.app_port=environ["APP_PORT"]

        self.picture_bucket=environ["PICTURE_BUCKET"]
        self.default_profile_pic_path=environ["DEFAULT_PROFILE_PIC_PATH"]
        self.default_hobby_pic_path=environ["DEFAULT_HOBBY_PIC_PATH"]