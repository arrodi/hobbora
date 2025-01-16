class Schemas:

    def __init__(self):        

        self.table_schemas = {
            "USER_ACCOUNTS": {
                "USER_ID": "text PRIMARY KEY",
                "EMAIL": "text",
                "USERNAME": "text",
                "FIRST_NAME": "text",
                "LAST_NAME": "text",
                "ABOUT": "text",
                "PASSWORD": "text",
                "TUTORING": "boolean",
                "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            },
            "USER_TUTOR_ACCOUNTS": {
                "TUTOR_ID": "text PRIMARY KEY",
                "USER_ID": "text REFERENCES USER_ACCOUNTS (USER_ID)",
                "RATING": "decimal",
                "EXPERIENCE": "text",
                "DESCRIPTION": "text",
                "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            },
            "USER_HOBBIES" : {
                "HOBBY_ID": "text PRIMARY KEY",
                "USER_ID": "text REFERENCES USER_ACCOUNTS (USER_ID)",
                "FACE_PICTURE_ID": "text", 
                "NAME": "text",
                "DESCRIPTION": "text",
                "PROFICIENCY": "text",
                "TUTORING": "boolean",
                "EXPERIENCE_YEARS": "integer",
                "EXPERIENCE_MONTHS": "integer",
                "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            },
            "USER_HOBBIES_TUTORING" : {
                "HOBBY_ID": "text REFERENCES USER_HOBBIES (HOBBY_ID)",
                "HOURLY_RATE": "integer",
                "LOCATION": "text",
                "MODE_LIVE_CALL": "boolean",
                "MODE_PUBLIC_IN_PERSON": "boolean",
                "MODE_PRIVATE_IN_PERSON": "boolean",
                "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            },
            "TUTORING_SESSION" : {
                "SESSION_ID": "text PRIMARY KEY",
                "USER_TUTOR_ID": "text REFERENCES USER_ACCOUNTS (USER_ID)",
                "USER_STUDENT_ID": "text REFERENCES USER_ACCOUNTS (USER_ID)",
                "SESSION_HOBBY": "text",
                "SESSION_MODE": "text",
                "SESSION_SCHEDULED_START_TIME": "TIMESTAMP",
                "SESSION_SCHEDULED_END_TIME": "TIMESTAMP",
                "SESSION_ACTUAL_START_TIME": "TIMESTAMP",
                "SESSION_ACTUAL_END_TIME": "TIMESTAMP",
            },
            "TUTORING_SESSION_REVIEWS" : {
                "REVIEW_ID": "text PRIMARY KEY",
                "USER_EMAIL": "text REFERENCES USER_ACCOUNTS (USER_ID)",
                "SESSION_ID": "text REFERENCES TUTORING_SESSION (SESSION_ID)",
                "SESSION_REVIEW_TEXT": "text",
                "SESSION_RATING": "integer"
            }
        }