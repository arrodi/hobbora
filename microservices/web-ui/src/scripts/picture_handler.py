from scripts.api import API
from scripts.settings import Settings

import base64
import logging

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()
picture_api = API(settings.picture_api_url)

def _get_default_profile_pic(picture_name):
    logger.info("Retrieving default profile picture")
    dict_payload = {"USER_ID": picture_name}
    api_return = picture_api.post_get_content("get_picture/profile_picture", dict_payload)

    if isinstance(api_return, bytes):
        return base64.b64encode(api_return).decode('utf-8')
    else:
        logger.warning("Default profile picture API response is not of type 'bytes'")
        return None

# Helper function to get the profile image
def get_profile_pic(session):
    logger.info("S3 client initialized successfully.")
    if not session.get('user'):
        return _get_default_profile_pic("default")
    else:
        dict_payload = {"USER_ID": session['user'].get('USER_ID')}
        api_return = picture_api.post_get_content("get_picture/profile_picture", dict_payload)
        if isinstance(api_return, bytes):
            # Process the returned image into a base64-encoded string
            return base64.b64encode(api_return).decode('utf-8')
        else:
            return _get_default_profile_pic("default")

def upload_profile_pic(session, files):
    user_id = session.get('user').get('USER_ID')
    api_return = picture_api.post_file(f"upload_picture/profile_picture/{user_id}", files=files)

    return api_return