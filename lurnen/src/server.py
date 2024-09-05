# STL IMPORTS
from os import environ

# EXT IMPORTS
from flask import Flask, render_template, request
from waitress import serve

# AUTHORED IMPORTS
import scripts.requests as requests
import scripts.encrypt as encrypt
from scripts.settings import Settings

import json

print("App Started!")
settings = Settings()

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
    db_password = requests.get(settings.api_url, f"/user_accounts/get_password?username={input_username}")["password"]

    if encrypt.check_password(input_password, db_password):
        return render_template("welcome.html", username = input_username)
    else:
        return render_template("wrong_password.html", username = input_username)
    
@app.route("/signup", methods=['POST'])
def signup_page():
    print(f"{request.remote_addr} signed up!")

    dict_payload = {}

    dict_payload["USER_NAME"] = request.form['username']
    dict_payload["USER_EMAIL"] = request.form['email']
    dict_payload["USER_PASS"] = encrypt.hash_password(request.form['password'])

    json_payload = json.dumps(dict_payload, indent=4)

    success_bool = requests.post(settings.api_url, f"/user_accounts/add_user", json_payload)

    if success_bool:
        return render_template("welcome.html", username = dict_payload["USER_NAME"])
    else:
        return render_template("home.html")


@app.route("/about", methods=['GET'])
def about_page():
    print(f"{request.remote_addr} visited ABOUT!")
    db_info_json = requests.get(settings.api_url, "")
    return render_template("about.html", db_info = str(db_info_json))

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host=settings.app_host, port=int(settings.app_port))