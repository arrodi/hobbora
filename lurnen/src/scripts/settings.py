from os import environ

class Settings:
    def __init__(self):
        self.app_port=int(environ["APP_PORT"])
        self.app_host=environ["APP_HOST"]
        
        self.api_url=environ["API_URL"]
        