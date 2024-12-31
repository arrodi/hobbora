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
        logger.info(f"get: GET request to: {full_url}")
        try:
            response = requests.get(full_url)
            logger.info(f"get: GET response status: {response.status_code}, of type {type(response.content)}")
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"get: Error during GET request to {full_url}: {e}")
            raise

    def post(self, api_endpoint, json_data=None, files=None):
        full_url = f'{self.url}/{api_endpoint}'
        logger.info(f"post_request: POST request to {full_url} with JSON: {type(json_data)}, Files: {type(files)}")
        if files:
            response = requests.post(full_url, files=files)
        else:
            response = requests.post(full_url, json=json_data)
        
        logger.info(f"post_request: POST response status: {response.status_code}, Content-Type: {response.headers.get('Content-Type')}")
        response.raise_for_status()
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        return response.content
