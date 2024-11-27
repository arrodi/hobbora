# STL IMPORTS
import os
import uuid
from io import BytesIO
import base64

# EXT IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session
from waitress import serve

# AUTHORED IMPORTS
import scripts.picture_handler as picture_handler
import scripts.encrypt as encrypt
from scripts.api import API
from scripts.settings import Settings

import json
from datetime import timedelta

print("WEB PORTAL STARTED")
settings = Settings()
db_api = API(settings.db_api_url)

# FLASK INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Required to encrypt session cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout

def render_with_user(page, **kwargs):
    print("###############")
    print(page)
    print(session.get('user'))
    print("###############")
    if session.get('user'):
        kwargs['encoded_image'] = picture_handler.get_profile_pic(session)
        kwargs['config'] = settings.config
        kwargs['user'] = session.get('user')
    else:
        kwargs['encoded_image'] = b''
        kwargs['config'] = settings.config
        kwargs['user'] = {}
    return render_template(page, **kwargs)

print("commit")

#########################
##### SERVER ROUTES #####
#########################
@app.route("/", methods=['GET'])
def home_page():
    return render_with_user("pages/home.html")

@app.route("/sign-in", methods=['GET', 'POST'])
def signin_page():
    if session.get('user'):
        return redirect(url_for('home_page'))
    
    if request.method == 'POST':
        dict_payload = {
            "USER_EMAIL": request.form['USER_EMAIL'],
            "USER_PASS": request.form['USER_PASS']
        }

        api_return = db_api.post(f"/user_accounts/get_user/email", dict_payload)
        user_data = api_return["USER_INFO"]

        if api_return["USER_EXISTS"]:
            if encrypt.check_password(dict_payload["USER_PASS"], user_data["USER_PASS"]):
                session["user"] = user_data
                session.modified = True
                return redirect(url_for('home_page'))
            else:
                error_message = "Incorrect password. Please try again!"
        else:
            error_message = "No Email Found! Try Again or Sign Up!"
        
        return render_with_user("pages/signin.html", error_message=error_message)

    return render_with_user("pages/signin.html")
    
@app.route("/sign-up", methods=['GET', 'POST'])
def signup_page():
    if session.get('user'):
        return redirect(url_for('home_page'))
    
    if request.method == 'POST':
        dict_payload = {
            "USER_ID": str(uuid.uuid4().hex[:6]),
            "USER_NAME": request.form['USER_NAME'],
            "USER_EMAIL": request.form['USER_EMAIL'],
            "USER_PASS": encrypt.hash_password(request.form['USER_PASS']),
            "USER_TUTOR": False
        }

        query_response = db_api.post(f"/user_accounts/add_user", dict_payload)
        
        if query_response["INSERT"] == "SUCCESS":
            session["user"] = dict_payload
            session.modified = True
            return redirect(url_for('home_page'))
        
        error_message = query_response.get("MESSAGE", "Unknown error. Please try again!")
        return render_with_user("pages/signup.html", error_message=error_message)

    return render_with_user("pages/signup.html")

@app.route("/account", methods=['GET'])
def account():
    return redirect(url_for('account_profile'))
    
@app.route("/account/profile", methods=['GET'])
def account_profile():
    if not session.get('user'):
        return redirect(url_for('signin_page'))
    
    api_return = db_api.post(f"/user_accounts/get_user/email", session.get('user'))
    print("######################")
    print("######################")
    print(api_return)
    print("######################")
    print("######################")
    user_data = api_return['USER_INFO']
    user_data.update(session.get('user'))
    return render_with_user("pages/account/profile/profile.html", user=user_data)
    
@app.route("/account/profile/edit/picture", methods=['GET', 'POST'])
def account_profile_edit_picture():
    if not session.get('user'):
        return redirect(url_for('signin_page'))

    if request.method == 'POST':
        file = request.files['file']
        files = {'file': (file.filename, file.stream, file.content_type)}
        picture_handler.upload_profile_pic(session, files)
        
        return redirect(url_for('account_profile'))

    if request.method == 'GET':
        return render_with_user("pages/account/profile/edit/picture.html")
    
@app.route("/account/profile/edit/description", methods=['GET', 'POST'])
def account_profile_edit_description():
    if not session.get('user'):
        return redirect(url_for('signin_page'))
    
    if request.method == 'POST':

        dict_payload = request.form.to_dict()
        print(dict_payload)

        session.get('user').update(dict_payload)
        print(session.get('user'))
        # PUT CHANGING THE DESCRIPTION API CALLS HERE
        print("PUT CHANGING THE DESCRIPTION API CALLS HERE")
        user_data = db_api.post(f"/user_accounts/edit_user", session.get('user'))
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(user_data)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        return redirect(url_for('account_profile'))

    if request.method == 'GET':
        api_return = db_api.post(f"/user_accounts/get_user/email", session.get('user'))
        user_data = api_return['USER_INFO']
        return render_with_user("pages/account/profile/edit/description.html", user=user_data)
    
@app.route('/account/become-tutor', methods=['GET', 'POST'])
def become_tutor():
    if not session.get('user'):
        return redirect(url_for('signin_page'))

    if session.get('user').get("USER_TUTOR"):
        return redirect(url_for('account'))

    if request.method == 'POST':
        return redirect(url_for('account'))
    
    return redirect(url_for('user_agreement'))
    
@app.route('/account/become-tutor/user_agreement', methods=['GET', 'POST'])
def user_agreement():
    if not session.get('user'):
        return redirect(url_for('signin_page'))
    
    if request.method == 'POST':
        request_dict = dict(session.get('user'))
        request_dict["USER_TUTOR"] = True
        query_response = db_api.post(f"/user_accounts/become_tutor", request_dict)

        if query_response["MODIFY"] == "SUCCESS":
            session["user"]['USER_TUTOR'] = True
            session.modified = True
            return redirect(url_for('become_tutor'))
        else:
            return redirect(url_for('home_page'))
    
    return render_with_user("user_agreement.html")
    
@app.route("/account/hobbies", methods=['GET'])
def account_hobbies():
    if not session.get('user'):
        return redirect(url_for('signin_page'))
    
    hobby_data = db_api.post(f"/user_hobbies/get_hobbies", session.get('user'))["DATA"]
    return render_with_user("pages/account/hobbies/hobbies.html", hobbies=hobby_data)

@app.route('/account/hobbies/hobby/<hobby_id>', methods=['GET', 'POST'])
def view_hobby(hobby_id):
    if not session.get('user'):
        return redirect(url_for('signin_page'))

    request_dict = session.get('user')
    request_dict["HOBBY_ID"] = str(hobby_id)

    user_data = db_api.post(f"/user_hobbies/get_hobby", request_dict)
    picture_urls = settings.default_pictures_urls

    return render_with_user('pages/account/hobbies/hobby/view.html', hobby=user_data["DATA"][0], picture_urls=picture_urls)

    
@app.route("/account/hobbies/hobby/add", methods=['GET', 'POST'])
def add_hobby():
    encoded_image = picture_handler.get_profile_pic(session)
    if session.get('user'):
        if request.method == 'POST':

            dict_payload = dict(request.form)
            dict_payload["USER_ID"] = session.get('user').get("USER_ID")

            print(dict_payload)

            db_api.post(f"/user_hobbies/add_hobby", dict_payload)

            return redirect(url_for('account_hobbies'))
        else:
            return render_template('pages/account/hobbies/hobby/add.html',user = session.get('user'), encoded_image=encoded_image)
    else:
        return redirect(url_for('signin_page'))
    
@app.route('/account/hobbies/hobby/edit/<hobby_id>', methods=['GET', 'POST'])
def edit_hobby(hobby_id):
    encoded_image = picture_handler.get_profile_pic(session)
    if session.get('user'):
        if request.method == 'GET':

            request_dict = dict(session.get('user'))
            request_dict["HOBBY_ID"] = str(hobby_id)

            user_data = db_api.post(f"/user_hobbies/get_hobby", request_dict)

        if request.method == 'POST':
            # Update hobby logic here
            return redirect(url_for('account'))
        
        return render_template('pages/account/hobbies/hobby/edit.html', user = session.get('user'), hobby=user_data["DATA"][0], encoded_image=encoded_image)
    else:
        return redirect(url_for('signin_page'))

@app.route('/account/hobbies/hobby/pictures/<hobby_id>', methods=['GET', 'POST'])
def pictures_hobby(hobby_id):
    if session.get('user'):
        print(f"/account/hobbies/hobby/pictures/{hobby_id}")
        if request.method == 'GET':
            request_dict = dict(session.get('user'))
            request_dict["HOBBY_ID"] = str(hobby_id)

            hobby_data = db_api.post(settings.db_api_url, f"/user_hobbies/get_hobby", request_dict)

            print(hobby_data)

            hobby_data = hobby_data["DATA"]
            for _hobby in hobby_data:
                user_id = {}
                request_dict["HOBBY_ID"] = _hobby['USER_ID']
                api_return = db_api.post_get_content(f"get_picture/hobby_picture", user_id)
            return render_template('hobby/pictures.html', user = session.get('user'), hobby = hobby_data)
        if request.method == 'POST':
            user_id = session.get('user').get('USER_ID')
            file = request.files['file']
            files = {'file': (file.filename, file.stream, file.content_type)}

            print("UPLOADING A PICTURE")

            api_return = db_api.post_file(f"upload_picture/hobby_picture/{user_id}/{hobby_id}", files=files)

            request_dict = {}
            request_dict["HOBBY_ID"] = hobby_id
            request_dict["PICTURE_ID"] = api_return["PICTURE_ID"]

            print(request_dict)

            hobby_data = db_api.post(settings.db_api_url, f"/user_hobbies/add_picture", request_dict)

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

                user_data = db_api.post(settings.db_api_url, f"/user_hobbies/get_hobby", request_dict)

                print("----------------------API---------------------")
                print(user_data)
                print("----------------------------------------------")

                return render_template('hobby/tutor.html', user = session.get('user'), hobby=user_data["DATA"][0])

            if request.method == 'POST':

                print("POST")

                request_form_dict = dict(request.form)
                request_form_dict["HOBBY_ID"] = str(hobby_id)

                print(request_form_dict)

                db_api.post(settings.db_api_url, f"/user_hobbies/tutor_hobby", request_form_dict)
                return redirect(url_for('account_hobbies'))
        else:
            print("HERE 3")
            return redirect(url_for('view_hobby', hobby_id = hobby_id))
    else:
        return redirect(url_for('signin_page'))
    
@app.route('/account/sessions', methods=['GET', 'POST'])
def account_sessions():
    if session.get('user'):
        dict_payload = {
            "USER_ID":session.get('user').get('USER_ID')
        }
        
        api_return = db_api.post_get_content(f"get_picture/profile_picture", dict_payload)
        if api_return:
            print("IMAGE RETURN")
            encoded_image = base64.b64encode(api_return).decode('utf-8')
            default_image= ''
        else:
            print("NO IMAGE RETURN")
            encoded_image=''
            default_image = 'images/default_pfp.jpg'

        sessions_data = db_api.post(settings.db_api_url, f"/user_sessions/get_sessions", session.get('user'))["DATA"]

        return render_template("account/sessions.html", user = session.get('user'), sessions=sessions_data, default_image=default_image, encoded_image=encoded_image)
    else:
        return redirect(url_for('signin_page'))

@app.route("/catalog", methods=['GET'])
def catalog_page():
    print("catalog")
    print(f"{request.remote_addr} visited Tutor-Catalog!")
    hobby_data = db_api.post(settings.db_api_url, f"/user_hobbies/get_tutored_hobbies", dict(session))
    hobby_data = hobby_data["DATA"]


    for _hobby in hobby_data:
        user_id = {}
        user_id['USER_ID'] = _hobby['USER_ID']
        api_return = db_api.post_get_content(f"get_picture/profile_picture", user_id)
        user_data = db_api.post(settings.db_api_url, f"/user_accounts/get_user/user_id", user_id)
        if api_return:
            _hobby['USER_PICTURE'] = base64.b64encode(api_return).decode('utf-8')
        if user_data:
            _hobby['USER'] = user_data

    if session.get('user'):

        return render_template("pages/catalog/catalog.html", user = session.get('user'), hobbies = hobby_data)
    return render_template("pages/catalog/catalog.html", user = session.get('user'), hobbies = hobby_data)

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

        hobby_data = db_api.post(settings.db_api_url, f"/user_hobbies/get_hobby", request_dict)['DATA'][0]

        print(hobby_data)

        user_id = {}
        user_id['USER_ID'] = hobby_data['USER_ID']
        api_return = db_api.post_get_content(f"get_picture/profile_picture", user_id)
        user_data = db_api.post(settings.db_api_url, f"/user_accounts/get_user/user_id", user_id)
        if api_return:
            hobby_data['USER_PICTURE'] = base64.b64encode(api_return).decode('utf-8')
        if user_data:
            hobby_data['USER'] = user_data

        if session.get('user').get('USER_ID') == hobby_data["USER_ID"]:
            return redirect(url_for('view_hobby', hobby_id = hobby_id))
        else:
            return render_template("pages/catalog/hobby/view.html", user = session.get('user'), hobby = hobby_data, picture_urls=picture_urls)
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