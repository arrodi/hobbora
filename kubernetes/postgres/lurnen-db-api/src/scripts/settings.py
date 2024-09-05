from os import environ

class Settings:
    def __init__(self):
        self.db_name=environ["DB_NAME"]
        self.db_user=environ["DB_USER"]
        self.db_password=environ["DB_PASSWORD"]
        self.db_host=environ["DB_HOST"]
        self.db_port=environ["DB_PORT"]
        
        self.app_host=environ["APP_HOST"]
        self.app_port=environ["APP_PORT"]