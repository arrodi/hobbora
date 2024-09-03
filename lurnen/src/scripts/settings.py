from os import environ

class Settings:
    def __init__(self):
        self.app_port=int(environ["APP_PORT"])
        
        self.api_url=environ["API_URL"]