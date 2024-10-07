# AUTHORED IMPORTS
import scripts.requests as requests

class Hobby:
    def __init__(self, user_info):
        self.id = user_info["HOBBY_ID"]
        self.email = user_info["USER_EMAIL"]
        self.name = user_info["HOBBY_NAME"]
        self.description = user_info["HOBBY_DESCRIPTION"]
        self.proficiency = user_info["HOBBY_PROFICIENCY"]
        self.tutoring = user_info["HOBBY_TUTORING"]
        self.experience_years = user_info["EXPERIENCE_YEARS"]
        self.experience_months = user_info["EXPERIENCE_MONTHS"]

    def to_dict(self):
        return {
            'HOBBY_ID': self.id,
            'USER_EMAIL': self.email,
            'HOBBY_NAME': self.name,
            'HOBBY_DESCRIPTION': self.description,
            'HOBBY_PROFICIENCY': self.proficiency,
            'HOBBY_TUTORING': self.tutoring,
            'EXPERIENCE_YEARS': self.experience_years,
            'EXPERIENCE_MONTHS': self.experience_months
        }
