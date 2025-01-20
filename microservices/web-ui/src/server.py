# EXT IMPORTS
from waitress import serve


from datetime import timedelta
import logging

from scripts.util.imports import *
from scripts.routes.auth import auth_bp
from scripts.routes.hobby import hobby_bp
from scripts.routes.account import account_bp
from scripts.routes.catalog import catalog_bp
from scripts.routes.session import session_bp
from scripts.routes.payment import payment_bp



settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FLASK INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Required to encrypt session cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(hobby_bp, url_prefix='/account/hobby')
app.register_blueprint(account_bp, url_prefix='/account')
app.register_blueprint(catalog_bp, url_prefix='/catalog')
app.register_blueprint(session_bp, url_prefix='/session')
app.register_blueprint(payment_bp, url_prefix='/payment')


@app.before_request
def load_globals():
    # Assign settings to g

    g.settings = settings
    # Assign logging to g
    
    g.logger = logger

    # Load current_user into g if user is in session
    if 'user' in session:
        print(session['user'])
        g.current_user = User(username=session['user']['USERNAME'])
    else:
        g.current_user = None
#########################
##### SERVER ROUTES #####
#########################
@app.route("/", methods=['GET'])
def home_page():
    logger.info(" ------- HOME ------- ")
    return dr.dynamic_render("pages/home.html")

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('images/favicon.png')

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host=settings.app_host, port=int(settings.app_port))
