# routes/user_routes.py
from scripts.util.imports import *

metadata_bp = Blueprint("metadata", __name__)
logger = logging.getLogger(__name__)


@metadata_bp.route("/hobby/id", methods=['POST'])
def get_picture_id():
    request_data = request.get_json()
    user_id = request_data.get("USER_ID")
    hobby_id = request_data.get("HOBBY_ID")
    folder_path = f"hobby_pictures/{user_id}/{hobby_id}/"
    file_paths = g.s3.retrieve_file_paths(g.settings.picture_bucket, folder_path)
    if file_paths:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully found list of pictures!"
        request_data["DATA"] = [_path.split("/")[-1].split(".")[0] for _path in file_paths]
    else:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Unable to find any pictures!"
        request_data["DATA"] = []

    return jsonify(request_data)