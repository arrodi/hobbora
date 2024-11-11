# STL IMPORTS
from datetime import datetime
import uuid
import io
import json

# EXT IMPORTS
from flask import Flask, jsonify, request, send_file, Response
from waitress import serve

# AUTHORED IMPORTS
from scripts.settings import Settings
from scripts.s3 import S3

settings = Settings()
s3 = S3(settings.s3_user, settings.s3_password, settings.s3_host)

# FLASK INIT                 
app = Flask(__name__)
print("API INITIALIZED")

#########################
##### SERVER ROUTES #####
#########################

@app.route("/test", methods=['GET'])
def test():
    print("HEALTHY!")
    return jsonify({"message": "test"})

@app.route("/profile_picture/get_picture", methods=['POST'])
def get_profile_picture():
    try:
        request_data = json.loads(request.get_json())
        user_id = request_data["USER_ID"]

        response = s3.client.get_object(Bucket=settings.picture_bucket, Key=f"profile_pictures/{user_id}.webp")
        image_data = response['Body'].read()
        # Create an in-memory file
        image_stream = io.BytesIO(image_data)
        return send_file(image_stream, mimetype='image/webp')
    except Exception as e:
        print(e)
        return Response(f"", status=500)
    
@app.route("/profile_picture/upload_picture/<user_id>", methods=['POST'])
def upload_profile_picture(user_id):

    file = request.files.get('file')
    filename = f"profile_pictures/{user_id}.webp"
    print(filename)
    try:
        s3.client.upload_fileobj(file, settings.picture_bucket, filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
        return jsonify({"message": f"File '{filename}' uploaded successfully to S3!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to upload the file: {str(e)}"}), 500
    
@app.route("/hobby_picture/get_picture", methods=['POST'])
def get_hobby_picture():
    try:
        request_data = json.loads(request.get_json())
        user_id = request_data["USER_ID"]
        hobby_id = request_data["HOBBY_ID"]
        picture_id = request_data["PICTURE_ID"]

        response = s3.client.get_object(Bucket=settings.picture_bucket, Key=f"hobby_pictures/{user_id}/{hobby_id}/{picture_id}.webp")
        image_data = response['Body'].read()
        # Create an in-memory file
        image_stream = io.BytesIO(image_data)
        return send_file(image_stream, mimetype='image/webp')
    except Exception as e:
        print(e)
        return Response(f"", status=500)

@app.route("/hobby_picture/upload_picture/<user_id>/<hobby_id>", methods=['POST'])
def upload_hobby_picture(user_id, hobby_id):
    print(f"hobby_picture/upload_picture/{user_id}/{hobby_id}")
    

    picture_id = str(uuid.uuid4().hex[:6])

    file = request.files.get('file')
    filename = f"hobby_pictures/{user_id}/{hobby_id}/{picture_id}.webp"
    print(filename)
    try:
        s3.client.upload_fileobj(file, settings.picture_bucket, filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
        return jsonify({"message": f"File '{filename}' uploaded successfully to S3!", "PICTURE_ID": picture_id}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to upload the file: {str(e)}"}), 500
#########################
##### SERVER BEGIN! #####
#########################

serve(app, host=settings.app_host, port=int(settings.app_port))