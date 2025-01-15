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

class Hobby:

    def __init__(self, id):
        logger.info(f"Initiating Hobby: {id}")
        if id:
            api_return = db_api.post(f"/hobby/get", {"HOBBY_ID": id})
        
        self.id = api_return.get("DATA").get("HOBBY_ID")
        
        self.face_picture_id = api_return.get("DATA").get("FACE_PICTURE_ID")

        self.name = api_return.get("DATA").get("NAME")
        self.description = api_return.get("DATA").get("DESCRIPTION")
        self.profeciency = api_return.get("DATA").get("PROFICIENCY")
        self.tutoring = api_return.get("DATA").get("TUTORING")
        self.experience_years = api_return.get("DATA").get("EXPERIENCE_YEARS")
        self.experience_months = api_return.get("DATA").get("EXPERIENCE_MONTHS")
        self.user_id = api_return.get("DATA").get("USER_ID")
        self.crt_dt = api_return.get("DATA").get("CRT_DT")
        self.upd_dt = api_return.get("DATA").get("UPD_DT")

        if self.tutoring:
            api_return = db_api.post(f"/hobby/tutored/get", {"HOBBY_ID": id})

            print(api_return)

            self.mode = {}
            self.mode_live_call = api_return.get("DATA").get("MODE_LIVE_CALL")
            self.mode_public_in_person = api_return.get("DATA").get("MODE_PUBLIC_IN_PERSON")
            self.mode_private_in_person = api_return.get("DATA").get("MODE_PRIVATE_IN_PERSON")
            self.hourly_rate = api_return.get("DATA").get("HOURLY_RATE")

    def get_json(self):
        return_dict = {
            "HOBBY_ID": self.id,
            "USER_ID": self.user_id,
            "FACE_PICTURE_ID": self.face_picture_id, 
            "NAME": self.name,
            "DESCRIPTION": self.description,
            "PROFICIENCY": self.profeciency,
            "TUTORING": self.tutoring,
            "EXPERIENCE_YEARS": self.experience_years,
            "EXPERIENCE_MONTHS": self.experience_months,
            "CRT_DT": self.crt_dt,
            "UPD_DT": self.upd_dt,
        }

        if self.tutoring:
            return_dict.update({
            "HOBBY_ID" : self.id,
            "MODE_LIVE_CALL": self.mode_live_call,
            "MODE_PUBLIC_IN_PERSON": self.mode_public_in_person,
            "MODE_PRIVATE_IN_PERSON": self.mode_private_in_person,
            "HOURLY_RATE": self.hourly_rate
        })

        print(return_dict)
        return return_dict
    
    def edit_picture(self, files, picture_id):
        logger.info(f"Uploading/Replacing hobby picture with id: {picture_id} for hobby {self.id}")
        if 'default' in picture_id or picture_id == None:
            logger.info(f"Uploading new picture")
            api_return = picture_api.post(f"upload_picture/hobby_picture/{self.user_id}/{self.id}", files=files)
        else:
            logger.info(f"Replacing previous picture")
            api_return = picture_api.post(f"upload_picture/hobby_picture/{self.user_id}/{self.id}/{picture_id}", files=files)

        if api_return["SUCCESS"]:
            return True
        else:
            return False
        
    def delete_picture(self, picture_id):
        logger.info(f"Deleting hobby picture with hobby id: {self.id} and picture id: {picture_id}")
        if 'default' not in picture_id:
            api_return = picture_api.get(f"delete_picture/hobby_picture/{self.user_id}/{self.id}/{picture_id}")
            print(api_return)
        else:
            return True, "The default picture cannot be deleted!"
        if api_return.json()["SUCCESS"]:
            return True, "Picture deleted successfully!"
        else:
            return False, "Failed to delete picture!"
        
    def get_pictures(self):
        logger.info(f"Fetching pictures for id {self.id}")
        picture_dict={"GRID_PICTURES":[],"FACE_PICTURE":{"id":"","bytes":""}}
        picture_ids = picture_api.post("/id/hobby/get", {"USER_ID":self.user_id, "HOBBY_ID":self.id})["DATA"]
        default_encoded_picture = base64.b64encode(picture_api.post("picture/hobby/get", {"USER_ID": "default", "HOBBY_ID": "default", "PICTURE_ID": "default_hobby"})).decode('utf-8')

        if picture_ids:
            for _pic_id in picture_ids:
                logger.info(f"Fetching picture for id {_pic_id}")
                payload = {}
                payload["USER_ID"] = self.user_id
                payload["HOBBY_ID"] = self.id
                payload["PICTURE_ID"] = _pic_id
                api_return = picture_api.post("picture/hobby/get", payload)
                if isinstance(api_return, bytes):
                    logger.info(f"Picture found")
                    encoded_picture = base64.b64encode(api_return).decode('utf-8')
                    if self.face_picture_id == _pic_id:
                        picture_dict['FACE_PICTURE'] = {"id":_pic_id, "bytes":encoded_picture}
                        picture_dict['GRID_PICTURES'].append({"id":_pic_id, "bytes":encoded_picture})
                    else:
                        picture_dict['GRID_PICTURES'].append({"id":_pic_id, "bytes":encoded_picture})
                else:
                    logger.info(f"get_hobby_pictures: Failed to fetch for id {_pic_id}")
                    if default_encoded_picture:
                        picture_dict['FACE_PICTURE'] = {"id":"default", "bytes":default_encoded_picture}
                        picture_dict['GRID_PICTURES'].extend([{"id": f"default{i}", "bytes": default_encoded_picture} for i in range(1, 11)])
            if picture_dict['FACE_PICTURE']["bytes"] == "" and picture_dict['GRID_PICTURES']:
                logger.info(f"No FACE_PICTURE picture found. Setting first GRID_PICTURES as main.")
                picture_dict['FACE_PICTURE']["id"] = picture_dict['GRID_PICTURES'][0]["id"]
                picture_dict['FACE_PICTURE']["bytes"] = picture_dict['GRID_PICTURES'][0]["bytes"]
        else:
            logger.info(f"Hobby picture list id is EMPTY")
            if default_encoded_picture:
                logger.info(f"Applying default picture")
                picture_dict['FACE_PICTURE'] = {"id":"default", "bytes":default_encoded_picture}
                picture_dict['GRID_PICTURES'].extend([{"id": f"default{i}", "bytes": default_encoded_picture} for i in range(1, 11)])
            else:
                logger.info(f"Default picture not found")

        grid_pic_len = len(picture_dict['GRID_PICTURES'])
        if grid_pic_len < 10:
            logger.info(f"GRID_PICTURES list is below 10 at {grid_pic_len}. Adding default pictures")
            if default_encoded_picture:
                picture_dict['GRID_PICTURES'].extend([{"id": f"default{i}", "bytes": default_encoded_picture} for i in range(1, 11-len(picture_dict['GRID_PICTURES']))])

        
        return picture_dict
    
    def edit_attributes(self, dict_payload):
        dict_payload["HOBBY_ID"] = self.id

        tutored_hobby_dict = {}
        tutored_hobby_dict["HOBBY_ID"] = self.id
        if self.tutoring:
            tutored_hobby_dict["MODE_LIVE_CALL"] = dict_payload.pop("MODE_LIVE_CALL", False)
            tutored_hobby_dict["MODE_PUBLIC_IN_PERSON"] = dict_payload.pop("MODE_PUBLIC_IN_PERSON", False)
            tutored_hobby_dict["MODE_PRIVATE_IN_PERSON"] = dict_payload.pop("MODE_PRIVATE_IN_PERSON", False)
            tutored_hobby_dict["HOURLY_RATE"] = dict_payload.pop("HOURLY_RATE", 0)

        print(tutored_hobby_dict)
        
        api_return = db_api.post(f"/hobby/tutored/edit", tutored_hobby_dict)

        if api_return["SUCCESS"]:
            self.mode_live_call = tutored_hobby_dict.get("MODE_LIVE_CALL")
            self.mode_public_in_person = tutored_hobby_dict.get("MODE_PUBLIC_IN_PERSON")
            self.mode_private_in_person = tutored_hobby_dict.get("MODE_PRIVATE_IN_PERSON")
            self.hourly_rate = tutored_hobby_dict.get("HOURLY_RATE")

        else:
            logger.info(f"FAILURE: editing for id {self.id}")
            return False

        api_return = db_api.post(f"/hobby/edit", dict_payload)

        if api_return["SUCCESS"]:
            self.face_picture_id = dict_payload.get("FACE_PICTURE_ID")
            self.name = dict_payload.get("NAME")
            self.description = dict_payload.get("DESCRIPTION")
            self.profeciency = dict_payload.get("PROFICIENCY")
            self.tutoring = dict_payload.get("TUTORING")
            self.experience_years = dict_payload.get("EXPERIENCE_YEARS")
            self.experience_months = dict_payload.get("EXPERIENCE_MONTHS")
            self.user_id = dict_payload.get("USER_ID")
            self.crt_dt = dict_payload.get("CRT_DT")
            self.upd_dt = dict_payload.get("UPD_DT")

            logger.info(f"SUCCESS: editing for id {self.id}")
            return True
        else:
            logger.info(f"FAILURE: editing for id {self.id}")
            return False
        
    def tutor(self, dict_payload):

        dict_payload = dict(dict_payload)
        dict_payload["HOBBY_ID"] = self.id
        logger.info(f"Tutoring id {self.id}")
        api_return = db_api.post(f"/hobby/tutor", dict_payload)

        tutored_hobby_dict = {}
        tutored_hobby_dict["HOBBY_ID"] = self.id
        tutored_hobby_dict["MODE_LIVE_CALL"] = dict_payload.pop("MODE_LIVE_CALL", False)
        tutored_hobby_dict["MODE_PUBLIC_IN_PERSON"] = dict_payload.pop("MODE_PUBLIC_IN_PERSON", False)
        tutored_hobby_dict["MODE_PRIVATE_IN_PERSON"] = dict_payload.pop("MODE_PRIVATE_IN_PERSON", False)
        tutored_hobby_dict["HOURLY_RATE"] = dict_payload.pop("HOURLY_RATE", 0)

        api_return = db_api.post(f"/hobby/tutored/add", tutored_hobby_dict)
        

        print(api_return)

        if api_return["SUCCESS"]:
            self.mode_live_call = tutored_hobby_dict.get("MODE_LIVE_CALL")
            self.mode_public_in_person = tutored_hobby_dict.get("MODE_PUBLIC_IN_PERSON")
            self.mode_private_in_person = tutored_hobby_dict.get("MODE_PRIVATE_IN_PERSON")
            self.hourly_rate = tutored_hobby_dict.get("HOURLY_RATE")

        else:
            logger.info(f"FAILURE: tutoring for id {self.id}")
            return False

        api_return = db_api.post(f"/hobby/edit", dict_payload)

        if api_return["SUCCESS"]:
            self.name = dict_payload.get("NAME")
            self.description = dict_payload.get("DESCRIPTION")
            self.profeciency = dict_payload.get("PROFICIENCY")
            self.tutoring = True
            self.experience_years = dict_payload.get("EXPERIENCE_YEARS")
            self.experience_months = dict_payload.get("EXPERIENCE_MONTHS")
            self.user_id = dict_payload.get("USER_ID")
            self.crt_dt = dict_payload.get("CRT_DT")
            self.upd_dt = dict_payload.get("UPD_DT")

            logger.info(f"SUCCESS: tutoring for id {self.id}")
            return True
        else:
            logger.info(f"FAILURE: tutoring for id {self.id}")
            return False

    def delete(self):

        api_return = db_api.post(f"/hobby/tutored/delete", {"HOBBY_ID": self.id})
        api_return = db_api.post(f"/hobby/delete", {"HOBBY_ID": self.id})

        if api_return["SUCCESS"]:
            return True
        else:
            return False
            
    @staticmethod
    def create(data_dict):
        dict_payload = {
            "USER_ID": data_dict.get("USER_ID"),
            "FACE_PICTURE_ID": "",
            "NAME": data_dict.get("NAME"),
            "DESCRIPTION": data_dict.get("DESCRIPTION"),
            "PROFICIENCY": data_dict.get("PROFICIENCY"),
            "TUTORING": False,
            "EXPERIENCE_YEARS": data_dict.get("EXPERIENCE_YEARS"),
            "EXPERIENCE_MONTHS": data_dict.get("EXPERIENCE_MONTHS"),
        }

        api_return = db_api.post(f"/hobby/add", dict_payload)

        if api_return["SUCCESS"]:
            pass
        else:
            pass

        return api_return
    @staticmethod
    def get(filter_dict=None):
        
        api_return = db_api.get(f"/catalog/hobbies/get", filter_dict)

        return api_return["DATA"]