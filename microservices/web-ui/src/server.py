# STL IMPORTS
import os

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
app.config['SECRET_KEY'] = os.urandom(24) # Required to encrypt session cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout


#########################
##### SERVER ROUTES #####
#########################
@app.route("/", methods=['GET'])
def home_page():
    print(f"{request.remote_addr} visited HOME!")
    if session:
        username = session['USER_NAME']   
        return render_template("home.html", username = username)
    return render_template("home.html")

@app.route("/tutor-catalog", methods=['GET'])
def tutor_catalog_page():
    print(f"{request.remote_addr} visited Tutor-Catalog!")
    if session:

        return render_template("tutor_catalog.html", username = session['USER_NAME'])
    return render_template("tutor_catalog.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_page'))

@app.route("/my-account", methods=['GET'])
def my_account():
    if session:
        print(session)
        print(type(session))
        user_data = requests.post(settings.api_url, f"/user_accounts/get_user", dict(session))
        hobby_data = requests.post(settings.api_url, f"/user_hobbies/get_hobbies", dict(session))["DATA"]

        print(user_data)
        print(hobby_data)

        return render_template("my_account.html", username = session['USER_NAME'] , email = user_data['USER_EMAIL'], hobbies=hobby_data)
    else:
        return redirect(url_for('signin_page'))
    
@app.route("/add-hobby", methods=['GET', 'POST'])
def add_hobby():
    if request.method == 'POST':

        dict_payload = dict(request.form)
        dict_payload["USER_EMAIL"] = session["USER_EMAIL"]

        print(dict_payload)

        requests.post(settings.api_url, f"/user_hobbies/add_hobby", dict_payload)

        return redirect(url_for('my_account'))
    else:
        return render_template("add_hobby.html")
    
    

@app.route("/sign-in", methods=['GET', 'POST'])
def signin_page():
    if request.method == 'POST':
        print(f"{request.remote_addr} visited HOME!")

        dict_payload = {}
        dict_payload["USER_EMAIL"] =  request.form['email']
        dict_payload["USER_PASS"] = request.form['password']

        query_response = requests.post(settings.api_url, f"/user_accounts/get_user", dict_payload)

        if query_response["USER_EXISTS"]:
            if encrypt.check_password(dict_payload["USER_PASS"], query_response["USER_PASS"]):
                session['USER_NAME'] = query_response["USER_NAME"]
                session['USER_EMAIL'] = query_response["USER_EMAIL"]
                return redirect(url_for('home_page'))
            else:
                return render_template("signin.html", error_message="Incorrect password. Please Try Again!")
        else:
            return render_template("signin.html", error_message="No Email Found! Try Again or Sign Up!")
    return render_template("signin.html")
    
@app.route("/sign-up", methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':

        dict_payload = {}
        dict_payload["USER_NAME"] = request.form['username']
        dict_payload["USER_EMAIL"] = request.form['email']
        dict_payload["USER_PASS"] = encrypt.hash_password(request.form['password'])

        query_response = requests.post(settings.api_url, f"/user_accounts/add_user", dict_payload)
        
        if query_response["INSERT"] == "SUCCESS":
            session['USER_NAME'] = dict_payload["USER_NAME"]
            session["USER_EMAIL"] = dict_payload["USER_EMAIL"]
            return redirect(url_for('home_page'))
        elif query_response["INSERT"] == "INSERT ERROR":
            return render_template("signup.html", error_message="That email is already taken. Please sign in or make a new account!")
        else:
            return render_template("signup.html", error_message="Unknown error. Please try again!")

    return render_template("signup.html")

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host=settings.app_host, port=int(settings.app_port))