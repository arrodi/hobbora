# routes/user_routes.py
from scripts.util.imports import *

picture_bp = Blueprint("picture", __name__)
logger = logging.getLogger(__name__)

@picture_bp.route("/profile/get", methods=['POST'])
@picture_bp.route("/hobby/get", methods=['POST'])
def get_picture():
    # Handles image retrieval for both profile and hobby pictures.
    request_data = request.get_json()
    print(type(request_data))
    user_id = request_data.get("USER_ID")
    hobby_id = request_data.get("HOBBY_ID")
    picture_id = request_data.get("PICTURE_ID")
    
    filename = util.generate_filename(user_id, hobby_id, picture_id)
    logger.info(f"Fetching from S3: {filename}")
    status, file, message = g.s3.retrieve_image(g.settings.picture_bucket, filename)

    if isinstance(file, io.BytesIO):
        return send_file(file, mimetype='image/webp')
    return jsonify(message), 200

@picture_bp.route("/upload/profile/<user_id>", methods=['POST'])
@picture_bp.route("/upload/hobby/<user_id>/<hobby_id>", methods=['POST'])
@picture_bp.route("/upload/hobby/<user_id>/<hobby_id>/<picture_id>", methods=['POST'])
def upload_picture(user_id, hobby_id=None, picture_id=None):
    # Handles image uploads for both profile and hobby pictures.
    file = request.files.get('file')
    
    if hobby_id:
        if picture_id:
            filename = util.generate_filename(user_id, hobby_id, picture_id)
        else:
            picture_id = uuid.uuid4().hex[:6]
            filename = util.generate_filename(user_id, hobby_id, picture_id)
    else:
        picture_id = None
        filename = util.generate_filename(user_id)

    logger.info(f"Uploading to S3: {filename}")
    status, message = g.s3.upload_file(file, g.settings.picture_bucket, filename)

    response = {}
    if status:
        response["SUCCESS"] = True
        response["MESSAGE"] = message
        response["PICTURE_ID"] = picture_id
    else:
        response["SUCCESS"] = False
        response["MESSAGE"] = message
        response["PICTURE_ID"] = ""
    return jsonify(response), 200

@picture_bp.route("/hobby/delete/<user_id>/<hobby_id>/<picture_id>", methods=['GET'])
def delete_picture(user_id, hobby_id=None, picture_id=None):
    if hobby_id:
        if picture_id:
            filename = util.generate_filename(user_id, hobby_id, picture_id)
            status, message = g.s3.delete_file(g.settings.picture_bucket, filename)

            response = {}
            if status:
                response["SUCCESS"] = True
                response["MESSAGE"] = message
                response["PICTURE_ID"] = picture_id
            else:
                response["SUCCESS"] = False
                response["MESSAGE"] = message
                response["PICTURE_ID"] = ""

            return jsonify(response), 200