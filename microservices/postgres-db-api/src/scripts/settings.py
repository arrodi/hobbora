from os import environ

class Settings:
    def __init__(self):
        self.db_name=environ["POSTGRES_DB"]
        self.db_user=environ["POSTGRES_USER"]
        self.db_password=environ["POSTGRES_PASSWORD"]
        self.db_host=environ["POSTGRES_HOST"]
        self.db_port=environ["POSTGRES_PORT"]
        
        self.app_host=environ["APP_HOST"]
        self.app_port=environ["APP_PORT"]