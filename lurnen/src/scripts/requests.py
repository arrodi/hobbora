import requests

def get(api_url, api_endpoint):
    
    response = requests.get(f'{api_url}{api_endpoint}')

    return response.json()