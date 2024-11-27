import requests
import json
import logging

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class API:

    def __init__(self, url):
        self.url = url
        logger.info(f"API initialized with base URL: {self.url}")

    def get(self, api_endpoint):
        full_url = f'{self.url}/{api_endpoint}'
        logger.info(f"GET request to: {full_url}")
        try:
            response = requests.get(full_url)
            logger.info(f"GET response status: {response.status_code}")
            logger.info(f"GET response of type {type(response)} and value of {str(response)}")
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error during GET request to {full_url}: {e}")
            raise

    def post_get_content(self, api_endpoint, json_data):
        json_data = json.dumps(json_data)
        full_url = f'{self.url}/{api_endpoint}'
        logger.info(f"POST request to: {full_url} with data: {json_data}")
        try:
            response = requests.post(full_url, json=json_data)
            logger.info(f"POST response status: {response.status_code}")
            logger.info(f"POST response of type {type(response)} and value of {str(response)}")
            if response.status_code != 200:
                return response.json()
            else:
                return response.content
        except requests.RequestException as e:
            logger.error(f"Error during POST request to {full_url}: {e}")
            raise

        
    def post(self, api_endpoint, json_data):
        full_url = f'{self.url}/{api_endpoint}'
        logger.info(f"POST request to: {full_url} with data: {json_data}")
        try:
            response = requests.post(full_url, json=json_data)
            logger.info(f"POST response status: {response.status_code}")
            logger.info(f"POST response of type {type(response)} and value of {str(response)}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error during POST request to {full_url}: {e}")
            raise

    def post_file(self, api_endpoint, files):
        full_url = f'{self.url}/{api_endpoint}'
        logger.info(f"POST file upload request to: {full_url} with files: {files.keys()}")
        try:
            response = requests.post(full_url, files=files)
            logger.info(f"POST file response status: {response.status_code}")
            logger.info(f"POST file response of type {type(response)} and value of {str(response)}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error during POST file upload to {full_url}: {e}")
            raise
