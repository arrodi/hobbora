# STL IMPORTS
from os import environ

# EXT IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session
from waitress import serve

# AUTHORED IMPORTS
import scripts.requests as requests
import scripts.encrypt as encrypt
from scripts.settings import Settings

import json
from datetime import timedelta

print("WEB PORTAL STARTED")
settings = Settings()

# FLASK INIT
app = Flask(__name__)
app.secret_key = 'your_secret_key' # Required to encrypt session cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout


#########################
##### SERVER ROUTES #####
#########################
@app.route("/", methods=['GET'])
def home_page():
    print(f"{request.remote_addr} visited HOME!")
    if 'user' in session:
        username = session['user']   
        return render_template("home.html", username = username)
    return render_template("home.html")

@app.route("/tutor-catalog", methods=['GET'])
def home_page():
    print(f"{request.remote_addr} visited Tutor-Catalog!")
    if 'user' in session:
        username = session['user']   
        return render_template("tutor_catalog.html", username = username)
    return render_template("tutor_catalog.html")

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    return redirect(url_for('home_page'))

@app.route("/my-account", methods=['GET'])
def my_account():
    if session:
        username = session['user'] 
        return render_template("my_account.html", username = username)
    else:
        return redirect(url_for('signin_page'))
    

@app.route("/sign-in", methods=['GET', 'POST'])
def signin_page():
    if request.method == 'POST':
        print(f"{request.remote_addr} visited HOME!")
        input_username =  request.form['username']
        input_password = request.form['password']
        db_password = requests.get(settings.api_url, f"/user_accounts/get_password?username={input_username}")["password"]
        print(f"api return: {db_password}")

        if db_password:
            if encrypt.check_password(input_password, db_password):
                session['user'] = input_username
                return redirect(url_for('home_page'))
            else:
                return render_template("signin.html", error_message="Incorrect password. Please Try Again!")
        else:
            return render_template("signin.html", error_message="No Username Found! Try Again or Sign Up!")
    return render_template("signin.html")
    
@app.route("/sign-up", methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':

        dict_payload = {}

        dict_payload["USER_NAME"] = request.form['username']
        dict_payload["USER_EMAIL"] = request.form['email']
        dict_payload["USER_PASS"] = encrypt.hash_password(request.form['password'])

        json_payload = json.dumps(dict_payload, indent=4)

        query_response = requests.post(settings.api_url, f"/user_accounts/add_user", json_payload)

        print(type(query_response))
        print(query_response)
        
        if query_response:
            session['user'] = dict_payload["USER_NAME"]
            return redirect(url_for('home_page'))
        else:
            return render_template("signup.html", error_message="That email is already taken. Please sign in or make a new account!")

    return render_template("signup.html")

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host=settings.app_host, port=int(settings.app_port))