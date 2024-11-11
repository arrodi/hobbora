# AUTHORED IMPORTS

class User():
    def __init__(self, user_info):
        self.user_id = user_info["USER_ID"]
        self.username = user_info["USER_NAME"]
        self.email = user_info["USER_EMAIL"]
        self.tutor = user_info["USER_TUTOR"]
    
    def to_dict(self):
        return {
            'USER_ID': self.user_id,
            'USER_NAME': self.username,
            'USER_EMAIL': self.email,
            'USER_TUTOR': self.tutor
        }