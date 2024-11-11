import requests
import json

def get(api_url, api_endpoint):
    
    print(f'{api_url}/{api_endpoint}')

    response = requests.get(f'{api_url}/{api_endpoint}')

    return response

def post_get_content(api_url, api_endpoint, json_data):
    json_string = json.dumps(json_data)

    print("POST REQUEST")
    print(f'{api_url}/{api_endpoint}')
    print(json_string)

    response = requests.post(f'{api_url}/{api_endpoint}', json=json_string)

    print("POST RESPONSE")
    print(response.status_code)
    print(type(response))
    print(type(response.content))
    
    return response.content

    
def post(api_url, api_endpoint, json_data):

    response = requests.post(f'{api_url}/{api_endpoint}', json=json_data)

    return response.json()

def post_file(api_url, api_endpoint, files):

    response = requests.post(f'{api_url}/{api_endpoint}', files=files)

    return response.json()
