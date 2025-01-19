from scripts.util.imports import *

session_bp = Blueprint('session', __name__)

@session_bp.route("", methods=['GET'])
def session():
    return redirect(url_for('profile'))