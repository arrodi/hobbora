from scripts.util.imports import *

payment_bp = Blueprint('payment', __name__)

@payment_bp.route("", methods=['GET'])
def payment():
    return redirect(url_for('profile'))