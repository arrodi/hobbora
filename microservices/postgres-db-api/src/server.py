from scripts.util.imports import *
from scripts.routes.user import user_bp
from scripts.routes.hobby import hobby_bp
from scripts.routes.catalog import catalog_bp


settings = Settings()
postgres = Postgres(settings.db_name, settings.db_user, settings.db_password, settings.db_host, settings.db_port)
postgres.prepare_db(queries, schemas)

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FLASK INIT                 
app = Flask(__name__)
print("API HAS BEEN INITIALIZED")

# Register Blueprints
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(hobby_bp, url_prefix="/hobby")
app.register_blueprint(catalog_bp, url_prefix="/catalog")

@app.before_request
def load_globals():

    g.settings = settings
    g.postgres = postgres
    g.logger = logger

#########################
##### SERVER BEGIN! #####
#########################

serve(app, host=settings.app_host, port=int(settings.app_port))
