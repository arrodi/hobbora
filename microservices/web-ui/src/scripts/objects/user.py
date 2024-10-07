# AUTHORED IMPORTS
import scripts.requests as requests

class User():
    def __init__(self, user_info):
        self.username = user_info["USER_NAME"]
        self.email = user_info["USER_EMAIL"]
        self.tutor = user_info["USER_TUTOR"]
    
    def to_dict(self):
        return {
            'USER_NAME': self.username,
            'USER_EMAIL': self.email,
            'USER_TUTOR': self.tutor
        }