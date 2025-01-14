# STL IMPORTS
import os
import uuid
from io import BytesIO
import base64

# EXT IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from waitress import serve

# AUTHORED IMPORTS
from scripts.util.api import API
from scripts.util.settings import Settings
from scripts.objects.user import User
from scripts.objects.hobby import Hobby

import json
from datetime import timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()
db_api = API(settings.db_api_url)
picture_api = API(settings.picture_api_url)

# FLASK INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Required to encrypt session cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout

def render_with_kwargs(page, **kwargs):
    logger.info(f"Rendering {page}")
    if session.get('user'):
        kwargs['encoded_image'] = current_user.get_profile_picture()
        kwargs['config'] = settings.config
        print(current_user.get_json)
        kwargs['user'] = current_user.get_json()
    else:
        kwargs['encoded_image'] = b''
        kwargs['config'] = settings.config
        kwargs['user'] = {}
    return render_template(page, **kwargs)

#########################
##### SERVER ROUTES #####
#########################
@app.route("/", methods=['GET'])
def home_page():
    logger.info(" ------- HOME ------- ")
    return render_with_kwargs("pages/home.html")

@app.route("/sign-in", methods=['GET', 'POST'])
def signin_page():
    logger.info(" ------- SIGN-IN ------- ")
    
    if session.get('user'):
        logger.info("User already signed in. Redirecting to the home page.")
        return redirect(url_for('home_page'))
    
    if request.method == 'GET':
        logger.info("Rendering sign-in page.")
        return render_with_kwargs("pages/signin.html")
    
    if request.method == 'POST':
        logger.info("Sign-in form submitted.")
        user_input_id = request.form['USER_INPUT']
        user_input_pass = request.form['PASSWORD']

        if len(user_input_id.split(".")) > 1:
            auth_check = User.authenticate(user_input_pass, email = user_input_id)
        else:
            auth_check = User.authenticate(user_input_pass, username = user_input_id)

        if auth_check["USER_EXISTS"]:
            if auth_check["USER_AUTHENTICATED"]:
                logger.info(f"Password verified for: {user_input_id}. Setting session.")
                global current_user
                if len(user_input_id.split(".")) > 1:
                    current_user = User(email = user_input_id)
                else:
                    current_user = User(username = user_input_id)
                session["user"] = current_user.get_json()
                session.modified = True
                return redirect(url_for('account_profile'))
            else:
                logger.warning(f"Password mismatch for: {user_input_id}")
                error_message = "Incorrect password. Please try again!"
        else:
            logger.warning(f"No user found for: {user_input_id}")
            error_message = "No Email Found! Try Again or Sign Up!"

        logger.info("Rendering sign-in page with error message.")
        return render_with_kwargs("pages/signin.html", error_message=error_message)

    
@app.route("/sign-up", methods=['GET', 'POST'])
def signup_page():
    if session.get('user'):
        return redirect(url_for('home_page'))
    
    if request.method == 'GET':
        return render_with_kwargs("pages/signup.html")
    
    if request.method == 'POST':
        create_response = User.create(request.form["USERNAME"], request.form["EMAIL"], request.form["PASSWORD"])
        
        if create_response["SUCCESS"]:
            global current_user
            current_user = User(username = request.form["USERNAME"])
            session["user"] = current_user.get_json()
            session.modified = True
            return redirect(url_for('home_page'))
        else:
            error_message = create_response.get("MESSAGE", "Unknown error. Please try again!")
            return render_with_kwargs("pages/signup.html", error_message=error_message)

@app.route("/account", methods=['GET'])
def account():
    return redirect(url_for('account_profile'))
    
@app.route("/account/profile", methods=['GET'])
def account_profile():
    logger.info(" ------- ACCOUNT/PROFILE ------- ")
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))
    else:
        return render_with_kwargs("pages/account/profile/profile.html")
    
@app.route("/account/profile/edit/picture", methods=['GET', 'POST'])
def account_profile_edit_picture():
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))
    
    if request.method == 'GET':
        return render_with_kwargs("pages/account/profile/edit/picture.html")

    if request.method == 'POST':
        file = request.files['file']
        files = {'file': (file.filename, file.stream, file.content_type)}
        upload_status = current_user.upload_profile_picture(files)
        
        if upload_status:
            return redirect(url_for('account_profile'))
        else:
            return redirect(url_for('account_profile_edit_picture'))
    
@app.route("/account/profile/edit/description", methods=['GET', 'POST'])
def account_profile_edit_description():
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))
    
    if request.method == 'GET':
        return render_with_kwargs("pages/account/profile/edit/description.html")
    
    if request.method == 'POST':
        
        edit_user_return = current_user.edit(request.form.to_dict())
        if edit_user_return["SUCCESS"]:
            session["user"] = current_user.get_json()
            session.modified = True
            return redirect(url_for('account_profile'))
        else:
            return render_with_kwargs("pages/account/profile/edit/description.html")

@app.route('/account/become-tutor', methods=['GET', 'POST'])
def become_tutor():
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))

    if session.get('user').get("TUTOR_STATUS"):
        return redirect(url_for('account'))

    if request.method == 'GET':
        return redirect(url_for('user_agreement'))

    if request.method == 'POST':
        return redirect(url_for('account'))
    
@app.route('/account/become-tutor/user_agreement', methods=['GET', 'POST'])
def user_agreement():
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))
    
    if request.method == 'GET':
        return render_with_kwargs('pages/account/profile/user_agreement.html')
    
    if request.method == 'POST':
        become_tutor_return = current_user.become_tutor()
        session["user"] = current_user.get_json()
        session.modified = True

        if become_tutor_return["SUCCESS"]:
            #TODO: ADD A SUCCESS MESSAGE
            return redirect(url_for('account'))
        else:
            #TODO: ADD A FAILURE MESSAGE
            return redirect(url_for('become_tutor'))
    
@app.route("/account/hobbies", methods=['GET'])
def account_hobbies():
    logger.info(" ------- ACCOUNT/HOBBIES ------- ")
    
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))
    
    try:
        print(current_user.get_hobby_ids)
        hobby_data = []
        for _hobby_id in current_user.get_hobby_ids():
            current_hobby = Hobby(_hobby_id)
            hobby_dict = current_hobby.get_json()
            try:
                hobby_dict.update(current_hobby.get_pictures())
                hobby_data.append(hobby_dict)
            except Exception as e:
                logger.exception(f"Error occurred while fetching pictures for hobby {current_hobby.id}: {str(e)}")
        
        logger.info("Successfully fetched hobbies data with pictures.")

        return render_with_kwargs("pages/account/hobbies/hobbies.html", hobbies=hobby_data)
    except Exception as e:
        logger.exception(f"An error occurred while fetching hobbies data: {str(e)}")
        return redirect(url_for('account_profile'))

@app.route("/account/hobbies/hobby/add", methods=['GET', 'POST'])
def add_hobby():
    logger.info(f" ------- ACCOUNT/HOBBIES/HOBBY/ADD ------- ")
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))
    
    if request.method == 'GET':
        return render_with_kwargs('pages/account/hobbies/hobby/add.html')
    
    if request.method == 'POST':
        dict_payload = dict(request.form)
        dict_payload["USER_ID"] = session.get('user').get("USER_ID")

        logger.info(f"Adding a hobby with info: {dict_payload}")

        create_response = Hobby.create(dict_payload)
        current_user.get_hobby_ids().append(create_response['HOBBY_ID'])

        if create_response["SUCCESS"]:
            return redirect(url_for('account_hobbies'))    
        else:
            return render_with_kwargs('pages/account/hobbies/hobby/add.html') 

        

@app.route('/account/hobbies/hobby/<hobby_id>', methods=['GET', 'POST'])
def view_hobby(hobby_id):
    logger.info(f" ------- ACCOUNT/HOBBIES/HOBBY/{hobby_id} ------- ")
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))

    if request.method == 'GET':
        current_hobby = Hobby(hobby_id)
        hobby_data = current_hobby.get_json()
        hobby_data.update(current_hobby.get_pictures())

    return render_with_kwargs('pages/account/hobbies/hobby/view.html', hobby=hobby_data)
    
@app.route('/account/hobbies/hobby/edit/<hobby_id>', methods=['GET', 'POST'])
def edit_hobby(hobby_id):
    
    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))

    if request.method == 'GET':
        logger.info(f" ------- GET: ACCOUNT/HOBBIES/HOBBY/EDIT/{hobby_id} ------- ")
        current_hobby = Hobby(hobby_id)
        hobby_data = current_hobby.get_json()

        return render_with_kwargs('pages/account/hobbies/hobby/edit.html', hobby=hobby_data)

    if request.method == 'POST':
        logger.info(f" ------- POST: ACCOUNT/HOBBIES/HOBBY/EDIT/{hobby_id} ------- ")
        dict_payload = dict(request.form)

        if not (dict_payload.get("MODE_LIVE_CALL", False) or dict_payload.get("MODE_PUBLIC_IN_PERSON", False) or dict_payload.get("MODE_PRIVATE_IN_PERSON", False)):
            ## TODO: add notification message component
            return redirect(url_for('edit_hobby', hobby_id=hobby_id))

        current_hobby = Hobby(hobby_id)
        
        update_successs = current_hobby.edit_attributes(dict_payload)

        if update_successs:
            return redirect(url_for('view_hobby', hobby_id=hobby_id))
        else:
            ## TODO: add notification message component
            return redirect(url_for('edit_hobby', hobby_id=hobby_id))

@app.route('/account/hobbies/hobby/pictures/<hobby_id>', methods=['GET', 'POST'])
def edit_hobby_pictures(hobby_id):
    

    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))

    if request.method == 'GET':
        logger.info(f" ------- GET: ACCOUNT/HOBBIES/HOBBY/PICTURES/{hobby_id} ------- ")
        current_hobby = Hobby(hobby_id)
        hobby_data = current_hobby.get_json()
        hobby_data.update(current_hobby.get_pictures())

        return render_with_kwargs('pages/account/hobbies/hobby/pictures.html', hobby = hobby_data)

    if request.method == 'POST':
        ##### PLACEHOLDER ######

        return redirect(url_for('edit_hobby_pictures', hobby_id = hobby_id))
    
@app.route('/account/hobbies/hobby/pictures/<hobby_id>/replace/<picture_id>', methods=['POST'])
def edit_hobby_pictures_replace(hobby_id, picture_id):
    logger.info(f" ------- ACCOUNT/HOBBIES/HOBBY/PICTURES/{hobby_id}/replace/{picture_id} ------- ")
    file = request.files.get('file')
    files = {'file': (file.filename, file.stream, file.content_type)}
    
    current_hobby = Hobby(hobby_id)
    update_successs = current_hobby.edit_picture(files, picture_id)

    if update_successs:  
        return jsonify(success=True, message="Picture replaced successfully!")
    else:
        return jsonify(success=False, message="Error!")

@app.route('/account/hobbies/hobby/pictures/<hobby_id>/delete/<picture_id>', methods=['GET'])
def delete_hobby_pictures(hobby_id, picture_id):
    logger.info(f" ------- ACCOUNT/HOBBIES/HOBBY/PICTURES/{hobby_id}/delete/{picture_id} ------- ")
    
    current_hobby = Hobby(hobby_id)
    update_successs, message = current_hobby.delete_picture(picture_id)

    if update_successs:
        return jsonify(success=True, message=message)
    else:
        return jsonify(success=False, message=message)

@app.route('/account/hobbies/hobby/tutor/<hobby_id>', methods=['GET', 'POST'])
def tutor_hobby(hobby_id):
    

    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))

    if session.get('user').get("TUTOR_STATUS"):
        current_hobby = Hobby(hobby_id)
        
        if request.method == 'GET':
            logger.info(f" ------- GET: ACCOUNT/HOBBIES/HOBBY/TUTOR/{hobby_id} ------- ")
            hobby_data = current_hobby.get_json()

            return render_with_kwargs('pages/account/hobbies/hobby/tutor.html', hobby=hobby_data)

        if request.method == 'POST':
            logger.info(f" ------- POST: ACCOUNT/HOBBIES/HOBBY/TUTOR/{hobby_id} ------- ")
            tutor_success = current_hobby.tutor(request.form)

            ##TODO add status messages to user
            if tutor_success:
                message = ""
            else:
                message = ""
            
            return redirect(url_for('account_hobbies'))
    else:
        ##TODO add status messages to user
        message = ""
        return redirect(url_for('view_hobby', hobby_id = hobby_id))
    
@app.route('/account/hobbies/hobby/delete/<hobby_id>', methods=['GET', 'POST'])
def delete_hobby(hobby_id):

    if not session.get('user'):
        logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('signin_page'))

    current_hobby = Hobby(hobby_id)
    if request.method == 'GET':
        logger.info(f" GET: ------- ACCOUNT/HOBBIES/HOBBY/DELETE/{hobby_id} ------- ")

        if current_hobby.user_id == session.get('user').get("USER_ID"):
            return render_with_kwargs('pages/account/hobbies/hobby/delete.html', hobby=current_hobby.get_json())
        else:
            ##Incase the user manually enters the url to delete a hobby that doesnt belong to them
            message = ""
            session.clear()
            return redirect(url_for('signin_page'))
        
    if request.method == 'POST':
        logger.info(f" GET: ------- ACCOUNT/HOBBIES/HOBBY/DELETE/{hobby_id} ------- ")
        if current_hobby.user_id == session.get('user').get("USER_ID"):
            delete_status = current_hobby.delete()

            if delete_status:
                message = ""
                return redirect(url_for('account_hobbies'))
            else:
                message = ""
                redirect(url_for('delete_hobby', hobby_id = hobby_id))
        else:
            message = ""
            return redirect(url_for('signin_page'))

@app.route("/catalog", methods=['GET'])
def catalog_page():
    hobby_data = db_api.post(f"/user_hobbies/get_tutored_hobbies", dict(session))
    hobby_data = hobby_data["DATA"]


    for _hobby in hobby_data:
        user_id = {}
        user_id['USER_ID'] = _hobby['USER_ID']
        api_return = db_api.post_get_content(f"get_picture/profile_picture", user_id)
        user_data = db_api.post(f"/user_accounts/get_user/user_id", user_id)
        if api_return:
            _hobby['USER_PICTURE'] = base64.b64encode(api_return).decode('utf-8')
        if user_data:
            _hobby['USER'] = user_data

    if session.get('user'):

        return render_with_kwargs("pages/catalog/catalog.html", user = session.get('user'), hobbies = hobby_data)
    return render_with_kwargs("pages/catalog/catalog.html", user = session.get('user'), hobbies = hobby_data)

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

        hobby_data = db_api.post(f"/hobby/get", request_dict)['DATA'][0]

        user_id = {}
        user_id['USER_ID'] = hobby_data['USER_ID']
        api_return = db_api.post_get_content(f"get_picture/profile_picture", user_id)
        user_data = db_api.post(f"/user_accounts/get_user/user_id", user_id)
        if api_return:
            hobby_data['USER_PICTURE'] = base64.b64encode(api_return).decode('utf-8')
        if user_data:
            hobby_data['USER'] = user_data

        if session.get('user').get('USER_ID') == hobby_data["USER_ID"]:
            return redirect(url_for('view_hobby', hobby_id = hobby_id))
        else:
            return render_with_kwargs("pages/catalog/hobby/view.html", user = session.get('user'), hobby = hobby_data, picture_urls=picture_urls)
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