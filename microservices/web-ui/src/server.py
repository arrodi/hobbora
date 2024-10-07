# STL IMPORTS
import os

# EXT IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session
from waitress import serve

# AUTHORED IMPORTS
import scripts.requests as requests
import scripts.encrypt as encrypt
from scripts.settings import Settings
from scripts.objects.hobby import Hobby
from scripts.objects.user import User

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
    if session.get('user'):
        return render_template("home.html", user = session["user"])
    return render_template("home.html", user = {})

@app.route("/sign-in", methods=['GET', 'POST'])
def signin_page():
    if session.get('user'):
        return render_template("home.html", user = session.get('user'))
    else:
        if request.method == 'POST':

            dict_payload = {}
            dict_payload["USER_EMAIL"] =  request.form['USER_EMAIL']
            dict_payload["USER_PASS"] = request.form['USER_PASS']

            query_response = requests.post(settings.api_url, f"/user_accounts/get_user", dict_payload)

            if query_response["USER_EXISTS"]:
                if encrypt.check_password(dict_payload["USER_PASS"], query_response["USER_PASS"]):
                    session["user"] = User(query_response).to_dict()
                    return redirect(url_for('home_page'))
                else:
                    return render_template("authentication/signin.html", user = {}, error_message="Incorrect password. Please Try Again!")
            else:
                return render_template("authentication/signin.html", user = {}, error_message="No Email Found! Try Again or Sign Up!")
        return render_template("authentication/signin.html", user = {})
    
@app.route("/sign-up", methods=['GET', 'POST'])
def signup_page():
    if session.get('user'):
        return render_template("home.html", user = session.get('user'))
    else:
        if request.method == 'POST':

            dict_payload = {}
            dict_payload["USER_NAME"] = request.form['USER_NAME']
            dict_payload["USER_EMAIL"] = request.form['USER_EMAIL']
            dict_payload["USER_PASS"] = encrypt.hash_password(request.form['USER_PASS'])
            dict_payload["USER_TUTOR"] = False

            query_response = requests.post(settings.api_url, f"/user_accounts/add_user", dict_payload)
            
            if query_response["INSERT"] == "SUCCESS":
                session["user"] = User(dict_payload).to_dict()
                return redirect(url_for('home_page'))
            elif query_response["INSERT"] == "ERROR":
                return render_template("authentication/signup.html", user = {}, error_message=query_response["MESSAGE"])
            else:
                return render_template("authentication/signup.html", user = {}, error_message="Unknown error. Please try again!")

        return render_template("authentication/signup.html", user = {})

@app.route("/account", methods=['GET'])
def account():
    if session:
        return redirect(url_for('account_profile'))
    else:
        return redirect(url_for('signin_page'))
    
@app.route("/account/profile", methods=['GET'])
def account_profile():
    if session.get('user'):

        pfp_url = 'images/default_pfp.jpg'

        user_data = requests.post(settings.api_url, f"/user_accounts/get_user", session.get('user'))

        return render_template("account/profile.html", user = session.get('user'), pfp_url=pfp_url)
    else:
        return redirect(url_for('signin_page'))
    
@app.route("/account/hobbies", methods=['GET'])
def account_hobbies():
    if session:

        pfp_url = 'images/default_pfp.jpg'

        user_data = requests.post(settings.api_url, f"/user_accounts/get_user", session.get('user'))
        hobby_data = requests.post(settings.api_url, f"/user_hobbies/get_hobbies", session.get('user'))["DATA"]

        session["hobbies"] = []
        for hobby in hobby_data:
            print(hobby)
            session["hobbies"].append(Hobby(hobby).to_dict())

        return render_template("account/hobbies.html", user = session.get('user'), hobbies=hobby_data, pfp_url=pfp_url)
    else:
        return redirect(url_for('signin_page'))

@app.route('/hobby/<hobby_id>', methods=['GET', 'POST'])
def view_hobby(hobby_id):


    if session:
        if request.method == 'GET':

            picture_urls = []

            if picture_urls:
                pass
            else:
                picture_urls = settings.default_pictures_urls

            print(picture_urls)

            request_dict = session.get('user')
            request_dict["HOBBY_ID"] = str(hobby_id)

            user_data = requests.post(settings.api_url, f"/user_hobbies/get_hobby", request_dict)

            print(user_data)

        if request.method == 'POST':
            # Update hobby logic here
            return redirect(url_for('my_account'))
        
        print(user_data["DATA"][0])
        return render_template('hobby/view.html', user = session.get('user'), hobby=user_data["DATA"][0], picture_urls=picture_urls)
    else:
        return redirect(url_for('signin_page'))

@app.route("/tutor-catalog", methods=['GET'])
def tutor_catalog_page():
    print(f"{request.remote_addr} visited Tutor-Catalog!")
    hobby_data = requests.post(settings.api_url, f"/user_hobbies/get_tutored_hobbies", dict(session))["DATA"]

    print(hobby_data)

    if session:

        return render_template("tutor_catalog.html", session = session, hobbies = hobby_data)
    return render_template("tutor_catalog.html", session=session, hobbies = hobby_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_page'))

    
@app.route("/add-hobby", methods=['GET', 'POST'])
def add_hobby():
    if session:
        if request.method == 'POST':

            dict_payload = dict(request.form)
            dict_payload["USER_EMAIL"] = session["USER_EMAIL"]

            print(dict_payload)

            requests.post(settings.api_url, f"/user_hobbies/add_hobby", dict_payload)

            return redirect(url_for('my_account'))
        else:
            return render_template("add_hobby.html",session=session)
    else:
        return redirect(url_for('signin_page'))
    
@app.route('/edit-hobby/<hobby_id>', methods=['GET', 'POST'])
def edit_hobby(hobby_id):

    if session:
        if request.method == 'GET':

            request_dict = dict(session)
            request_dict["HOBBY_ID"] = str(hobby_id)

            user_data = requests.post(settings.api_url, f"/user_hobbies/get_hobby", request_dict)

            print(user_data)

        if request.method == 'POST':
            # Update hobby logic here
            return redirect(url_for('my_account'))
        
        return render_template('edit_hobby.html', session=session, hobby=user_data["DATA"][0])
    else:
        return redirect(url_for('signin_page'))

@app.route('/tutor-hobby/<hobby_id>', methods=['GET', 'POST'])
def tutor_hobby(hobby_id):

    if session:
        if session["USER_TUTOR"]:
            if request.method == 'GET':

                request_dict = dict(session)
                request_dict["HOBBY_ID"] = str(hobby_id)

                user_data = requests.post(settings.api_url, f"/user_hobbies/get_hobby", request_dict)

                print(user_data)

                return render_template('tutor_hobby.html', session=session, hobby=user_data["DATA"][0])

            if request.method == 'POST':

                print("POST")

                request_form_dict = dict(request.form)
                request_form_dict["HOBBY_ID"] = str(hobby_id)

                print(request_form_dict)

                requests.post(settings.api_url, f"/user_hobbies/tutor_hobby", request_form_dict)
                return redirect(url_for('my_account'))
        else:
            return redirect(url_for('view_hobby', session=session, hobby_id = hobby_id))
    else:
        return redirect(url_for('signin_page'))

@app.route('/become-tutor', methods=['GET', 'POST'])
def become_tutor():
    if session:
        if request.method == 'GET':
            if session:
                if session["USER_TUTOR"]:
                    return redirect(url_for('my_account'))
                else:
                    return render_template("user_agreement.html")
            else:
                return render_template("signup.html")
        else:

            request_dict = dict(session)
            request_dict["USER_TUTOR"] = True
            query_response = requests.post(settings.api_url, f"/user_accounts/become_tutor", request_dict)
            print(query_response)
            if query_response["MODIFY"] == "SUCCESS":
                session['USER_TUTOR'] = True
                return redirect(url_for('my_account'))
            else:
                return redirect(url_for('home_page'))
    else:
        return redirect(url_for('signin_page'))

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host=settings.app_host, port=int(settings.app_port))