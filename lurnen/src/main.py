# STL IMPORTS
from os import environ

# EXT IMPORTS
from flask import Flask, render_template
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
    print("Someone visited HOME!")
    return render_template("home.html")

@app.route("/about", methods=['GET'])
def about():
    print("Someone visited ABOUT!")
    db_info_json = requests.get("postgres.postgres-api-service:5000", "")
    return render_template("about.html", db_info = str(db_info_json))

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host='0.0.0.0', port=int(environ["APP_PORT"]))