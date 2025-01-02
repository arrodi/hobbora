from scripts.api import API
from scripts.settings import Settings

import base64
import logging

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()
picture_api = API(settings.picture_api_url)

def _get_default_profile_picture():
    logger.info("_get_default_profile_picture: Retrieving default profile picture")
    dict_payload = {"USER_ID": "default"}
    api_return = picture_api.post("get_picture/profile_picture", dict_payload)

    if isinstance(api_return, bytes):
        return base64.b64encode(api_return).decode('utf-8')
    else:
        logger.warning("Default profile picture API response is not of type 'bytes'")
        return None
    
def _get_default_hobby_picture():
    logger.info("_get_default_hobby_picture: Retrieving default hobby picture")
    default_pic_json = {"USER_ID": "default", "HOBBY_ID": "default", "PICTURE_ID": "default_hobby"}
    api_return = picture_api.post("get_picture/hobby_picture", default_pic_json)
    return base64.b64encode(api_return).decode('utf-8')

# Helper function to get the profile image
def get_profile_picture(user_id):
    logger.info(f"Retrieving picture with {user_id}")
    if not user_id:
        return _get_default_profile_picture()
    else:
        dict_payload = {"USER_ID": user_id}
        api_return = picture_api.post("get_picture/profile_picture", dict_payload)
        if isinstance(api_return, bytes):
            # Process the returned image into a base64-encoded string
            return base64.b64encode(api_return).decode('utf-8')
        else:
            return _get_default_profile_picture()

def upload_profile_picture(user_id, files):
    logger.info(f"upload_profile_picture: Uploading profile picture with {user_id}")
    api_return = picture_api.post(f"upload_picture/profile_picture/{user_id}", files=files)

    return api_return

def upload_hobby_picture(files, user_id, hobby_id, picture_id):
    logger.info(f"upload_hobby_picture: Uploading hobby picture with hobby id: {hobby_id} and picture id: {picture_id}")
    if picture_id:
        api_return = picture_api.post(f"upload_picture/hobby_picture/{user_id}/{hobby_id}/{picture_id}", files=files)
    else:
        api_return = picture_api.post(f"upload_picture/hobby_picture/{user_id}/{hobby_id}", files=files)

    return api_return

def delete_hobby_picture(user_id, hobby_id, picture_id):
    logger.info(f"upload_hobby_picture: Deleting hobby picture with hobby id: {hobby_id} and picture id: {picture_id}")
    picture_api.get(f"delete_picture/hobby_picture/{user_id}/{hobby_id}/{picture_id}")


def get_hobby_pictures(_hobby):
    logger.info(f"get_hobby_pictures: Attaching pictures to hobby {_hobby.get('HOBBY_ID')}")
    hobby_id_lst = picture_api.post("get_picture_id/hobby", _hobby)
    _hobby['HOBBY_SECONDARY_PICTURES'] = []
    _hobby['HOBBY_MAIN_PICTURE'] = {}
    _hobby['HOBBY_MAIN_PICTURE']["id"] = ""
    _hobby['HOBBY_MAIN_PICTURE']["bytes"] = ""
    default_picture = _get_default_hobby_picture()

    if hobby_id_lst:
        logger.info(f"get_hobby_pictures: Hobby list id is not empty {hobby_id_lst}")
        for picture_id in hobby_id_lst:
            logger.info(f"get_hobby_pictures: Fetching picture for id {picture_id}")
            _hobby["PICTURE_ID"] = picture_id
            api_return = picture_api.post("get_picture/hobby_picture", _hobby)
            if isinstance(api_return, bytes):
                logger.info(f"get_hobby_pictures: Picture found")
                encoded_picture = base64.b64encode(api_return).decode('utf-8')
                if _hobby["HOBBY_MAIN_PICTURE_ID"] == picture_id:
                    _hobby['HOBBY_MAIN_PICTURE'] = {"id":picture_id, "bytes":encoded_picture}
                    _hobby['HOBBY_SECONDARY_PICTURES'].append({"id":picture_id, "bytes":encoded_picture})
                else:
                    _hobby['HOBBY_SECONDARY_PICTURES'].append({"id":picture_id, "bytes":encoded_picture})
            else:
                logger.info(f"get_hobby_pictures: Failed to fetch for id {picture_id}")
                # Assign default picture if API call fails
                if default_picture:
                    _hobby['HOBBY_MAIN_PICTURE'] = {"id":"default", "bytes":default_picture}
                    _hobby['HOBBY_SECONDARY_PICTURES'].extend([{"id": f"default{i}", "bytes": default_picture} for i in range(1, 11)])
    else:
        logger.info(f"get_hobby_pictures: Hobby list id is EMPTY")
        # No hobby IDs; use default picture
        if default_picture:
            _hobby['HOBBY_MAIN_PICTURE'] = {"id":"default", "bytes":default_picture}
            _hobby['HOBBY_SECONDARY_PICTURES'].extend([{"id": f"default{i}", "bytes": default_picture} for i in range(1, 11)])
    if not _hobby['HOBBY_MAIN_PICTURE']:
        logger.info(f"get_hobby_pictures: No main picture found. Setting first secondary picture as main.")
    
    if _hobby['HOBBY_SECONDARY_PICTURES']:
        _hobby['HOBBY_MAIN_PICTURE']["id"] = _hobby['HOBBY_SECONDARY_PICTURES'][0]["id"]
        _hobby['HOBBY_MAIN_PICTURE']["bytes"] = _hobby['HOBBY_SECONDARY_PICTURES'][0]["bytes"]
    
    if len(_hobby['HOBBY_SECONDARY_PICTURES']) < 10:
        logger.info(f"get_hobby_pictures: Secondary pictures list is below 10 at {str(len(_hobby["HOBBY_SECONDARY_PICTURES"]))}. Adding default pictures")
        if default_picture:
            _hobby['HOBBY_SECONDARY_PICTURES'].extend([{"id": f"default{i}", "bytes": default_picture} for i in range(1, 11-len(_hobby['HOBBY_SECONDARY_PICTURES']))])

    

    return _hobby

        
        