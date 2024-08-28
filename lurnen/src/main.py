# STL IMPORTS
from os import environ

# EXT IMPORTS
from flask import Flask, render_template, request
from waitress import serve

# AUTHORED IMPORTS
import scripts.requests as requests

print("App Started!")

# FLASK INIT
app = Flask(__name__)

#########################
##### SERVER ROUTES #####
#########################
@app.route("/", methods=['GET'])
def homepage():
    print(f"{request.remote_addr} visited HOME!")
    return render_template("home.html")

@app.route("/about", methods=['GET'])
def about():
    print(f"{request.remote_addr} visited ABOUT!")
    db_info_json = requests.get("http://postgres-api-service.postgres.svc.cluster.local:8080", "")
    return render_template("about.html", db_info = str(db_info_json))

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host='0.0.0.0', port=int(environ["APP_PORT"]))