# STL IMPORTS
import uuid
import logging
import io
import json

# EXT IMPORTS
from flask import Flask, jsonify, request, send_file, current_app
from waitress import serve
from io import BytesIO

# AUTHORED IMPORTS
from scripts.settings import Settings
from scripts.s3 import S3

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S3 CONFIG
settings = Settings()
s3 = S3(settings.s3_user, settings.s3_password, settings.s3_host)

# FLASK INIT                 
app = Flask(__name__)
logger.info("API INITIALIZED")

#########################
##### SERVER ROUTES #####
#########################
def upload_default_pfp():
    logger.info(f"Uploading default profile picture to S3")
    with open(settings.default_pic_path, "rb") as img_file:
        file_obj = BytesIO(img_file.read())
    filename = "profile_pictures/default.webp"
    response, status_code = s3.upload_file(file_obj, settings.picture_bucket, filename)
    logger.info(f"Uploading to S3 response: {response}")
    logger.info(f"Uploading to S3 status: {status_code}")

def generate_filename(user_id, hobby_id=None, picture_id=None):
    # Generates S3 key based on user, hobby, and picture identifiers.
    if hobby_id and picture_id:
        return f"hobby_pictures/{user_id}/{hobby_id}/{picture_id}.webp"
    return f"profile_pictures/{user_id}.webp"

#########################
###### APP STARTUP ######
#########################
upload_default_pfp()

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unexpected error occurred: {e}", exc_info=True)
    return jsonify({"error": "An internal error occurred."}), 500

@app.route("/get_picture/profile_picture", methods=['POST'])
@app.route("/get_picture/hobby_picture", methods=['POST'])
def get_picture():
    # Handles image retrieval for both profile and hobby pictures.
    request_data = json.loads(request.get_json())
    user_id = request_data.get("USER_ID")
    hobby_id = request_data.get("HOBBY_ID")
    picture_id = request_data.get("PICTURE_ID")
    
    filename = generate_filename(user_id, hobby_id, picture_id)
    logger.info(f"Fetching from S3: {filename}")
    response = s3.retrieve_image(settings.picture_bucket, filename)
    logger.info(f"S3 Return of type {type(response)} and value of {str(response)}")

    if isinstance(response, io.BytesIO):
        return send_file(response, mimetype='image/webp')
    return jsonify(response[0]), response[1]

@app.route("/upload_picture/profile_picture/<user_id>", methods=['POST'])
@app.route("/upload_picture/hobby_picture/<user_id>/<hobby_id>", methods=['POST'])
def upload_picture(user_id, hobby_id=None):
    # Handles image uploads for both profile and hobby pictures.
    file = request.files.get('file')
    
    
    if hobby_id:
        picture_id = uuid.uuid4().hex[:6]
        filename = generate_filename(user_id, hobby_id, picture_id)
    else:
        picture_id = None
        filename = generate_filename(user_id)

    logger.info(f"Uploading to S3: {filename}")
    response, status_code = s3.upload_file(file, settings.picture_bucket, filename)

    if picture_id and status_code == 200:
        response["PICTURE_ID"] = picture_id
    return jsonify(response), status_code

#########################
##### SERVER BEGIN! #####
#########################

serve(app, host=settings.app_host, port=int(settings.app_port))
