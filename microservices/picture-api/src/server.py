from scripts.util.imports import *
from scripts.routes.picture import picture_bp
from scripts.routes.metadata import metadata_bp

settings = Settings()
s3 = S3(settings.s3_user, settings.s3_password, settings.s3_host)

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FLASK INIT                 
app = Flask(__name__)
logger.info("API INITIALIZED")

# Register Blueprints
app.register_blueprint(picture_bp, url_prefix="/picture")
app.register_blueprint(metadata_bp, url_prefix="/metadata")

#Run Env Preparations
util.upload_default_pictures(logger, s3, settings)

@app.before_request
def load_globals():

    g.settings = settings
    g.logger = logger
    g.s3 = s3

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unexpected error occurred: {e}", exc_info=True)
    return jsonify({"error": "An internal error occurred."}), 500
        

#########################
##### SERVER BEGIN! #####
#########################

serve(app, host=settings.app_host, port=int(settings.app_port))
