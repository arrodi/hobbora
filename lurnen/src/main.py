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
def home_page():
    print(f"{request.remote_addr} visited HOME!")
    return render_template("home.html")

@app.route("/login", methods=['POST'])
def login_page():
    print(f"{request.remote_addr} visited HOME!")
    input_username =  request.form['username']
    input_password = request.form['password']
    db_password = requests.get("http://lurnen-db-api-service.postgres.svc.cluster.local:8080", f"get_password?username={input_username}")["password"]

    if db_password == input_password:
        return render_template("welcome.html", username = input_username)
    else:
        return render_template("wrong_password.html", username = input_username)

@app.route("/about", methods=['GET'])
def about_page():
    print(f"{request.remote_addr} visited ABOUT!")
    db_info_json = requests.get("http://lurnen-db-api-service.postgres.svc.cluster.local:8080", "")
    return render_template("about.html", db_info = str(db_info_json))

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host='0.0.0.0', port=int(environ["APP_PORT"]))