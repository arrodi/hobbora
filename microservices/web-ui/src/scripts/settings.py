import os

class Settings:
    def __init__(self):
        self.app_port=int(os.environ["APP_PORT"])
        self.app_host=os.environ["APP_HOST"]
        
        self.db_api_url=os.environ["DB_API_URL"]
        self.picture_api_url=os.environ["PICTURE_API_URL"]
        self.config = {"name":"Hobbora"}

        self.otel_collector_url=os.environ["OTEL_COLLECTOR_URL"]

    # def _get_all_paths_in_folder(self, directory):
    #     file_urls = []
    #     for filename in os.listdir(directory):
    #         # Get the full path
    #         file_path = os.path.join(directory, filename)
    #         if os.path.isfile(file_path):
    #             # Convert file path to a URL-like path (if needed)
    #             file_urls.append(file_path.replace('\\', "/").replace('microservices/web-ui/src/static/', ""))
    #     return file_urls