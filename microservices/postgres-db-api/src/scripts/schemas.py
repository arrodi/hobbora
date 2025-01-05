class Schemas:

    def __init__(self):        

        self.table_schemas = {
            "USER_ACCOUNTS": {
                "USER_ID": "text PRIMARY KEY",
                "USER_EMAIL": "text",
                "USER_NAME": "text",
                "USER_FIRST_NAME": "text",
                "USER_LAST_NAME": "text",
                "USER_ABOUT": "text",
                "USER_PASS": "text",
                "USER_TUTOR": "boolean",
                "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            },
            "USER_TUTOR_ACCOUNTS": {
                "TUTOR_ID": "text PRIMARY KEY",
                "USER_ID": "text REFERENCES USER_ACCOUNTS (USER_ID)",
                "TUTOR_RATING": "decimal",
                "TUTOR_EXPERIENCE": "text",
                "TUTOR_DESCRIPTION": "text",
                "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            },
            "USER_HOBBIES" : {
                "HOBBY_ID": "text PRIMARY KEY",
                "USER_ID": "text REFERENCES USER_ACCOUNTS (USER_ID)",
                "HOBBY_MAIN_PICTURE_ID": "text", 
                "HOBBY_NAME": "text",
                "HOBBY_DESCRIPTION": "text",
                "HOBBY_PROFICIENCY": "text",
                "HOBBY_TUTORING": "boolean",
                "EXPERIENCE_YEARS": "integer",
                "EXPERIENCE_MONTHS": "integer",
                "CRT_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "UPD_DT": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            },
            "USER_HOBBIES_TUTORING" : {
                "HOBBY_ID": "text REFERENCES USER_HOBBIES (HOBBY_ID)",
                "TUTORING_HOURLY_RATE": "integer",
                "TUTORING_MODE_LIVE_CALL": "boolean",
                "TUTORING_MODE_PUBLIC_IN_PERSON": "boolean",
                "TUTORING_MODE_PRIVATE_IN_PERSON": "boolean",
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