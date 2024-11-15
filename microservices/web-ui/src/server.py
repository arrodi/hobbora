# STL IMPORTS
import os
import uuid
from io import BytesIO
import base64

# EXT IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session
from waitress import serve

# AUTHORED IMPORTS
import scripts.api as api
import scripts.encrypt as encrypt
from scripts.settings import Settings
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

            query_response = api.post(settings.db_api_url, f"/user_accounts/get_user/email", dict_payload)

            if query_response["USER_EXISTS"]:
                if encrypt.check_password(dict_payload["USER_PASS"], query_response["USER_PASS"]):
                    session["user"] = User(query_response).to_dict()
                    session.modified = True 
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
            dict_payload["USER_ID"] = str(uuid.uuid4().hex[:6])
            dict_payload["USER_NAME"] = request.form['USER_NAME']
            dict_payload["USER_EMAIL"] = request.form['USER_EMAIL']
            dict_payload["USER_PASS"] = encrypt.hash_password(request.form['USER_PASS'])
            dict_payload["USER_TUTOR"] = False

            query_response = api.post(settings.db_api_url, f"/user_accounts/add_user", dict_payload)
            
            if query_response["INSERT"] == "SUCCESS":
                session["user"] = User(dict_payload).to_dict()
                session.modified = True 
                return redirect(url_for('home_page'))
            elif query_response["INSERT"] == "ERROR":
                return render_template("authentication/signup.html", user = {}, error_message=query_response["MESSAGE"])
            else:
                return render_template("authentication/signup.html", user = {}, error_message="Unknown error. Please try again!")

        return render_template("authentication/signup.html", user = {})

@app.route("/account", methods=['GET'])
def account():
    if session.get('user'):
        return redirect(url_for('account_profile'))
    else:
        return redirect(url_for('signin_page'))
    
@app.route("/account/profile", methods=['GET'])
def account_profile():
    if session.get('user'):

        user_id = {}
        user_id["USER_ID"] = session.get('user').get('USER_ID')
        
        print(user_id)
        api_return = api.post_get_content(settings.picture_api_url, f"get_picture/profile_picture", user_id)
        if api_return:
            encoded_image = base64.b64encode(api_return).decode('utf-8')
            default_image= ''
        else:
            encoded_image=''
            default_image = 'images/default_pfp.jpg'

        user_data = api.post(settings.db_api_url, f"/user_accounts/get_user/email", session.get('user'))

        return render_template("account/profile.html", user = session.get('user'), default_image=default_image, encoded_image=encoded_image)
    else:
        return redirect(url_for('signin_page'))
    
@app.route("/account/profile/edit", methods=['GET', 'POST'])
def account_profile_edit():
    if session.get('user'):
        if request.method == 'POST':
            user_id = session.get('user').get('USER_ID')
            file = request.files['file']
            user_data = api.post(settings.db_api_url, f"/user_accounts/get_user/email", session.get('user'))
            files = {'file': (file.filename, file.stream, file.content_type)}
            api.post_file(settings.picture_api_url, f"upload_picture/profile_picture/{user_id}", files=files)
            return redirect(url_for('account_profile'))
        if request.method == 'GET':
            return render_template("account/profile-edit.html", user = session.get('user'))
    else:
        return redirect(url_for('signin_page'))
    
@app.route("/account/hobbies", methods=['GET'])
def account_hobbies():
    if session.get('user'):

        user_id = {}
        user_id["USER_ID"] = session.get('user').get('USER_ID')
        
        api_return = api.post_get_content(settings.picture_api_url, f"get_picture/profile_picture", user_id)
        if api_return:
            print("IMAGE RETURN")
            encoded_image = base64.b64encode(api_return).decode('utf-8')
            default_image= ''
        else:
            print("NO IMAGE RETURN")
            encoded_image=''
            default_image = 'images/default_pfp.jpg'

        hobby_data = api.post(settings.db_api_url, f"/user_hobbies/get_hobbies", session.get('user'))["DATA"]

        return render_template("account/hobbies.html", user = session.get('user'), hobbies=hobby_data, default_image=default_image, encoded_image=encoded_image)
    else:
        return redirect(url_for('signin_page'))
    
@app.route('/account/become-tutor', methods=['GET', 'POST'])
def become_tutor():
    if session.get('user'):
        print(session.get('user'))
        if request.method == 'GET':
            print(session.get('user').get("USER_TUTOR"))
            if session.get('user').get("USER_TUTOR"):
                print(session.get('user').get("USER_TUTOR"))
                return redirect(url_for('account'))
            else:
                return redirect(url_for('user_agreement'))
        if request.method == 'POST':
            return redirect(url_for('account'))
    else:
        return redirect(url_for('signin_page'))
    
@app.route('/account/become-tutor/user_agreement', methods=['GET', 'POST'])
def user_agreement():
    if session.get('user'):
        if request.method == 'GET':
            return render_template("user_agreement.html", user = session.get('user'))
        if request.method == 'POST':
            request_dict = dict(session.get('user'))
            request_dict["USER_TUTOR"] = True
            query_response = api.post(settings.db_api_url, f"/user_accounts/become_tutor", request_dict)
            if query_response["MODIFY"] == "SUCCESS":
                
                session["user"]['USER_TUTOR'] = True
                session.modified = True
                print("success!")
                print(session)
                return redirect(url_for('become_tutor'))
            else:
                return redirect(url_for('home_page'))
    else:
        return redirect(url_for('signin_page'))

@app.route('/account/hobbies/hobby/<hobby_id>', methods=['GET', 'POST'])
def view_hobby(hobby_id):
    if session.get('user'):
        if request.method == 'GET':

            picture_urls = []

            if picture_urls:
                pass
            else:
                picture_urls = settings.default_pictures_urls

            request_dict = session.get('user')
            request_dict["HOBBY_ID"] = str(hobby_id)

            user_data = api.post(settings.db_api_url, f"/user_hobbies/get_hobby", request_dict)
            print(session.get('user'))
            print(user_data["DATA"][0])
            print(picture_urls)
        return render_template('hobby/view.html', user = session.get('user'), hobby=user_data["DATA"][0], picture_urls=picture_urls)
    else:
        return redirect(url_for('signin_page'))
    
@app.route("/account/hobbies/hobby/add", methods=['GET', 'POST'])
def add_hobby():
    if session.get('user'):
        if request.method == 'POST':

            dict_payload = dict(request.form)
            dict_payload["USER_ID"] = session.get('user').get("USER_ID")

            print(dict_payload)

            api.post(settings.db_api_url, f"/user_hobbies/add_hobby", dict_payload)

            return redirect(url_for('account_hobbies'))
        else:
            return render_template("hobby/add.html",user = session.get('user'))
    else:
        return redirect(url_for('signin_page'))
    
@app.route('/account/hobbies/hobby/edit/<hobby_id>', methods=['GET', 'POST'])
def edit_hobby(hobby_id):

    if session.get('user'):
        if request.method == 'GET':

            request_dict = dict(session.get('user'))
            request_dict["HOBBY_ID"] = str(hobby_id)

            user_data = api.post(settings.db_api_url, f"/user_hobbies/get_hobby", request_dict)

        if request.method == 'POST':
            # Update hobby logic here
            return redirect(url_for('account'))
        
        return render_template('hobby/edit.html', user = session.get('user'), hobby=user_data["DATA"][0])
    else:
        return redirect(url_for('signin_page'))

@app.route('/account/hobbies/hobby/pictures/<hobby_id>', methods=['GET', 'POST'])
def pictures_hobby(hobby_id):
    if session.get('user'):
        print(f"/account/hobbies/hobby/pictures/{hobby_id}")
        if request.method == 'GET':
            request_dict = dict(session.get('user'))
            request_dict["HOBBY_ID"] = str(hobby_id)

            hobby_data = api.post(settings.db_api_url, f"/user_hobbies/get_hobby", request_dict)

            print(hobby_data)

            hobby_data = hobby_data["DATA"]
            for _hobby in hobby_data:
                user_id = {}
                request_dict["HOBBY_ID"] = _hobby['USER_ID']
                api_return = api.post_get_content(settings.picture_api_url, f"get_picture/hobby_picture", user_id)
            return render_template('hobby/pictures.html', user = session.get('user'), hobby = hobby_data)
        if request.method == 'POST':
            user_id = session.get('user').get('USER_ID')
            file = request.files['file']
            files = {'file': (file.filename, file.stream, file.content_type)}

            print("UPLOADING A PICTURE")

            api_return = api.post_file(settings.picture_api_url, f"upload_picture/hobby_picture/{user_id}/{hobby_id}", files=files)

            request_dict = {}
            request_dict["HOBBY_ID"] = hobby_id
            request_dict["PICTURE_ID"] = api_return["PICTURE_ID"]

            print(request_dict)

            hobby_data = api.post(settings.db_api_url, f"/user_hobbies/add_picture", request_dict)

            return redirect(url_for('pictures_hobby', hobby_id = hobby_id))
    else:
        return redirect(url_for('signin_page'))

@app.route('/account/hobbies/hobby/tutor/<hobby_id>', methods=['GET', 'POST'])
def tutor_hobby(hobby_id):

    
    if session.get('user'):
        print(session.get('user').get("USER_TUTOR"))
        if session.get('user').get("USER_TUTOR"):
            print("HERE 1")
            if request.method == 'GET':
                print("HERE 2")
                request_dict = dict(session.get('user'))
                request_dict["HOBBY_ID"] = str(hobby_id)

                user_data = api.post(settings.db_api_url, f"/user_hobbies/get_hobby", request_dict)

                print("----------------------API---------------------")
                print(user_data)
                print("----------------------------------------------")

                return render_template('hobby/tutor.html', user = session.get('user'), hobby=user_data["DATA"][0])

            if request.method == 'POST':

                print("POST")

                request_form_dict = dict(request.form)
                request_form_dict["HOBBY_ID"] = str(hobby_id)

                print(request_form_dict)

                api.post(settings.db_api_url, f"/user_hobbies/tutor_hobby", request_form_dict)
                return redirect(url_for('account_hobbies'))
        else:
            print("HERE 3")
            return redirect(url_for('view_hobby', hobby_id = hobby_id))
    else:
        return redirect(url_for('signin_page'))

@app.route("/catalog", methods=['GET'])
def catalog_page():
    print("catalog")
    print(f"{request.remote_addr} visited Tutor-Catalog!")
    hobby_data = api.post(settings.db_api_url, f"/user_hobbies/get_tutored_hobbies", dict(session))
    hobby_data = hobby_data["DATA"]


    for _hobby in hobby_data:
        user_id = {}
        user_id['USER_ID'] = _hobby['USER_ID']
        api_return = api.post_get_content(settings.picture_api_url, f"get_picture/profile_picture", user_id)
        user_data = api.post(settings.db_api_url, f"/user_accounts/get_user/user_id", user_id)
        if api_return:
            _hobby['USER_PICTURE'] = base64.b64encode(api_return).decode('utf-8')
        if user_data:
            _hobby['USER'] = user_data

    if session.get('user'):

        return render_template("catalog/catalog.html", user = session.get('user'), hobbies = hobby_data)
    return render_template("catalog/catalog.html", user = session.get('user'), hobbies = hobby_data)

@app.route("/catalog/hobby/<hobby_id>", methods=['GET'])
def catalog_hobby(hobby_id):
    if session.get('user'):
        request_dict = {}
        request_dict["HOBBY_ID"] = str(hobby_id)

        picture_urls = []

        if picture_urls:
            pass
        else:
            picture_urls = settings.default_pictures_urls

        hobby_data = api.post(settings.db_api_url, f"/user_hobbies/get_hobby", request_dict)

        if session.get('user').get('USER_ID') == hobby_data["DATA"][0]["USER_ID"]:
            return redirect(url_for('view_hobby', hobby_id = hobby_id))
        else:
            return render_template("catalog/hobby.html", user = session.get('user'), hobby = hobby_data["DATA"][0], picture_urls=picture_urls)
    else:
           return redirect(url_for('signin_page'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home_page'))

    


#########################
##### SERVER BEGIN! #####
#########################
serve(app, host=settings.app_host, port=int(settings.app_port))