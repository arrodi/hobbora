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
    logger.info(f"Retrieving picture with {session}")
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
    logger.info(f"Uploading profile picture with {session}")
    user_id = session.get('user').get('USER_ID')
    api_return = picture_api.post_file(f"upload_picture/profile_picture/{user_id}", files=files)

    return api_return

def attach_hobby_main_pictures(_hobby):
    logger.info(f"Attaching pictures to hobby {_hobby}")
    hobby_id_lst = picture_api.post_get_content(f"get_picture_id/hobby", _hobby)
    if hobby_id_lst:
        for _id in hobby_id_lst:
            if _hobby["HOBBY_MAIN_PICTURE_ID"] == _id:
                _hobby["PICTURE_ID"] = _id
                api_return = picture_api.post_get_content(f"get_picture/hobby_picture", _hobby)
                if api_return:
                    _hobby['HOBBY_PICTURE'] = base64.b64encode(api_return).decode('utf-8')
    else:
        default_pic_json = {"USER_ID":"default","HOBBY_ID":"default","PICTURE_ID":"default_hobby"}
        api_return = picture_api.post_get_content(f"get_picture/hobby_picture", default_pic_json)
        if api_return:
                    _hobby['HOBBY_PICTURE'] = base64.b64encode(api_return).decode('utf-8') 
    return _hobby
        
        