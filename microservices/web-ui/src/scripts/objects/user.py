import base64
import logging

from scripts.util.api import API
from scripts.util.settings import Settings

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LOCAL MODULES CONFIG
settings = Settings()
db_api = API(settings.db_api_url)
picture_api = API(settings.picture_api_url)

class User:

    def __init__(self, email=None, username=None):
        if email:
            api_return = db_api.post(f"user/get", {"EMAIL": email})
        if username:
            api_return = db_api.post(f"user/get", {"USERNAME": username})
        
        self.id = api_return.get("DATA").get("USER_ID")

        self.email = api_return.get("DATA").get("EMAIL")
        self.username = api_return.get("DATA").get("USERNAME")
        self.first_name = api_return.get("DATA").get("FIRST_NAME")
        self.last_name = api_return.get("DATA").get("LAST_NAME")
        self.about = api_return.get("DATA").get("ABOUT")
        self.tutor_status = api_return.get("DATA").get("TUTOR_STATUS")
        self.crt_dt = api_return.get("DATA").get("CRT_DT")
        self.upd_dt = api_return.get("DATA").get("UPD_DT")


    
    def edit(self, data_dict):
        logger.info(f"Making changes to {self.id}, changes: {data_dict}")
        data_dict["USER_ID"] = self.id
        api_return = db_api.post(f"user/edit", data_dict)

        if api_return["SUCCESS"]:
            self.first_name = data_dict.get("FIRST_NAME")
            self.last_name = data_dict.get("LAST_NAME")
            self.about = data_dict.get("ABOUT")

        return api_return
    
    def become_tutor(self,):
        api_return = db_api.post(f"user/tutor/become", {"USER_ID": self.id})
        
        if api_return["SUCCESS"]:
            self.tutor_status = True

        return api_return


    def get_json(self):
        return_dict = {
            "USER_ID": self.id,
            "EMAIL": self.email,
            "USERNAME": self.username,
            "FIRST_NAME": self.first_name,
            "LAST_NAME": self.last_name,
            "TUTOR_STATUS": self.tutor_status,
            "ABOUT": self.about,
            "CRT_DT": self.crt_dt,
            "UPD_DT": self.upd_dt,
        }
        
        return return_dict

    def get_profile_picture(self):
        logger.info(f"Retrieving profile picture for user: {self.id}")
        api_return = picture_api.post("picture/profile/get", {"USER_ID": self.id})

        if isinstance(api_return, bytes):
            logger.info("Succesfully retrieved profile picture")
            return base64.b64encode(api_return).decode('utf-8')
        else:
            logger.info("Retrieving default profile picture")
            api_return = picture_api.post("picture/profile/get", {"USER_ID": "default"})
            
            if isinstance(api_return, bytes):
                logger.info("Succesfully retrieved DEFAULT profile picture")
                return base64.b64encode(api_return).decode('utf-8')
            else:
                logger.warning("Default profile picture API response is not of type 'bytes'")
                return None
    
    def upload_profile_picture(self, files):
        logger.info(f"Uploading profile picture with {self.id}")
        api_return = picture_api.post(f"upload_picture/profile_picture/{self.id}", files=files)

        if api_return["SUCCESS"]:
            return True
        else:
            return False

    def get_hobby_ids(self):
        api_return = db_api.post(f"user/hobbies/get_ids", {"USER_ID": self.id})["HOBBY_IDS"]

        return api_return

    def __del__(self):
        print(f"Instance {self.username} is being destroyed.")

    @staticmethod
    def create(username, email, password):
        logger.info(f"Creating user: {username} with email: {email}")
        dict_payload = {
            "USERNAME": username,
            "EMAIL": email,
            "PASSWORD": password,
        }

        api_response = db_api.post(f"/user/create", dict_payload)

        if api_response["SUCCESS"]:
            logger.info(f"SUCCESS: Created user: {username} result: {api_response}")
            pass
        else:
            logger.info(f"FAILED: Did not create user: {username} result: {api_response}")
            pass

        return api_response

    @staticmethod
    def authenticate(input_password, email=None, username=None):
        logger.info(f"Authenticating user: {username} with email: {email}")
        if email:
            api_return = db_api.post(f"/user/authenticate", {"EMAIL": email, "PASSWORD": input_password})
        if username:
            api_return = db_api.post(f"/user/authenticate", {"USERNAME": username, "PASSWORD": input_password})

        logger.info(f"Authenticating result: {api_return}")

        return api_return
    
    
        