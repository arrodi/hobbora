# EXT IMPORTS
import logging
from datetime import timedelta

import redis
from flask_session import Session
from waitress import serve
from werkzeug.middleware.proxy_fix import ProxyFix

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

# Trust one upstream proxy (Ingress/Load Balancer) so Flask correctly handles
# HTTPS scheme and secure cookies when TLS terminates before the pod.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# IMPORTANT: shared key across pods for consistent cookie signing.
app.config['SECRET_KEY'] = settings.secret_key

# Store session data in Redis so any pod can read the same user session.
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(settings.redis_url)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=settings.session_lifetime_minutes)

# Cookie carries only the session id; data is in Redis.
app.config['SESSION_COOKIE_NAME'] = settings.session_cookie_name
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = settings.session_cookie_secure
app.config['SESSION_COOKIE_SAMESITE'] = settings.session_cookie_samesite

# Avoid creating sessions for anonymous visitors unless we explicitly use session.
app.config['SESSION_USE_SIGNER'] = True

Session(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(hobby_bp, url_prefix='/account/hobby')
app.register_blueprint(account_bp, url_prefix='/account')
app.register_blueprint(catalog_bp, url_prefix='/catalog')
app.register_blueprint(session_bp, url_prefix='/session')
app.register_blueprint(payment_bp, url_prefix='/payment')


@app.before_request
def load_globals():
    # Assign settings and logger to g
    g.settings = settings
    g.logger = logger

    # Load current_user into g if user is in session
    if 'user' in session:
        g.current_user = User(username=session['user']['USERNAME'])
    else:
        g.current_user = None


#########################
##### SERVER ROUTES #####
#########################
@app.route('/', methods=['GET'])
def home_page():
    success_message = request.args.get('success_message')
    error_message = request.args.get('error_message')
    logger.info(' ------- HOME ------- ')
    return dr.dynamic_render('pages/home.html', success_message=success_message, error_message=error_message)


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('images/favicon.png')


#########################
##### SERVER BEGIN! #####
#########################
serve(app, host=settings.app_host, port=int(settings.app_port))
