from scripts.util.imports import *

hobby_bp = Blueprint('hobby', __name__)

@hobby_bp.route('add', methods=['GET', 'POST'])
def add():
    g.logger.info(f" ------- ACCOUNT/HOBBIES/HOBBY/ADD ------- ")
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))
    
    if request.method == 'GET':
        return dr.dynamic_render('pages/hobby/add.html')
    
    if request.method == 'POST':
        dict_payload = dict(request.form)
        dict_payload["USER_ID"] = session.get('user').get("USER_ID")

        g.logger.info(f"Adding a hobby with info: {dict_payload}")

        create_response = Hobby.create(dict_payload)
        g.current_user.get_hobby_ids().hobby_bpend(create_response['HOBBY_ID'])

        if create_response["SUCCESS"]:
            return redirect(url_for('account.hobbies'))    
        else:
            return dr.dynamic_render('pages/hobby/add.html') 

        

@hobby_bp.route('view/<hobby_id>', methods=['GET', 'POST'])
def view(hobby_id):
    g.logger.info(f" ------- ACCOUNT/HOBBIES/HOBBY/{hobby_id} ------- ")
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))

    if request.method == 'GET':
        current_hobby = Hobby(hobby_id)
        hobby_data = current_hobby.get_json()
        hobby_data.update(current_hobby.get_pictures())

    return dr.dynamic_render('pages/hobby/view.html', hobby=hobby_data)
    
@hobby_bp.route('edit/<hobby_id>', methods=['GET', 'POST'])
def edit(hobby_id):
    
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))

    if request.method == 'GET':
        g.logger.info(f" ------- GET: ACCOUNT/HOBBIES/HOBBY/EDIT/{hobby_id} ------- ")
        current_hobby = Hobby(hobby_id)
        hobby_data = current_hobby.get_json()

        return dr.dynamic_render('pages/hobby/edit.html', hobby=hobby_data)

    if request.method == 'POST':
        g.logger.info(f" ------- POST: ACCOUNT/HOBBIES/HOBBY/EDIT/{hobby_id} ------- ")
        dict_payload = dict(request.form)

        current_hobby = Hobby(hobby_id)

        if current_hobby.tutoring:
            if not (dict_payload.get("MODE_LIVE_CALL", False) or dict_payload.get("MODE_PUBLIC_IN_PERSON", False) or dict_payload.get("MODE_PRIVATE_IN_PERSON", False)):
                ## TODO: add notification message component
                return redirect(url_for('hobby.edit', hobby_id=hobby_id))
        
        update_successs = current_hobby.edit_attributes(dict_payload)

        if update_successs:
            return redirect(url_for('hobby.view', hobby_id=hobby_id))
        else:
            ## TODO: add notification message component
            return redirect(url_for('hobby.edit', hobby_id=hobby_id))

@hobby_bp.route('pictures/<hobby_id>/edit', methods=['GET', 'POST'])
def pictures_edit(hobby_id):
    

    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))

    if request.method == 'GET':
        g.logger.info(f" ------- GET: ACCOUNT/HOBBIES/HOBBY/PICTURES/{hobby_id} ------- ")
        current_hobby = Hobby(hobby_id)
        hobby_data = current_hobby.get_json()
        hobby_data.update(current_hobby.get_pictures())

        return dr.dynamic_render('pages/hobby/pictures.html', hobby = hobby_data)

    if request.method == 'POST':
        ##### PLACEHOLDER ######

        return redirect(url_for('hobby.pictures_edit', hobby_id = hobby_id))
    
@hobby_bp.route('pictures/<hobby_id>/replace/<picture_id>', methods=['POST'])
def picture_replace(hobby_id, picture_id):
    g.logger.info(f" ------- ACCOUNT/HOBBIES/HOBBY/PICTURES/{hobby_id}/replace/{picture_id} ------- ")
    file = request.files.get('file')
    files = {'file': (file.filename, file.stream, file.content_type)}
    
    current_hobby = Hobby(hobby_id)
    update_successs = current_hobby.edit_picture(files, picture_id)

    if update_successs:  
        return jsonify(success=True, message="Picture replaced successfully!")
    else:
        return jsonify(success=False, message="Error!")

@hobby_bp.route('pictures/<hobby_id>/delete/<picture_id>', methods=['GET'])
def picture_delete(hobby_id, picture_id):
    g.logger.info(f" ------- ACCOUNT/HOBBIES/HOBBY/PICTURES/{hobby_id}/delete/{picture_id} ------- ")
    
    current_hobby = Hobby(hobby_id)
    update_successs, message = current_hobby.delete_picture(picture_id)

    if update_successs:
        return jsonify(success=True, message=message)
    else:
        return jsonify(success=False, message=message)

@hobby_bp.route('tutor/<hobby_id>', methods=['GET', 'POST'])
def tutor(hobby_id):
    

    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))

    if g.current_user.tutoring:
        current_hobby = Hobby(hobby_id)
        
        if request.method == 'GET':
            g.logger.info(f" ------- GET: ACCOUNT/HOBBIES/HOBBY/TUTOR/{hobby_id} ------- ")
            hobby_data = current_hobby.get_json()

            return dr.dynamic_render('pages/hobby/tutor.html', hobby=hobby_data)

        if request.method == 'POST':
            g.logger.info(f" ------- POST: ACCOUNT/HOBBIES/HOBBY/TUTOR/{hobby_id} ------- ")
            tutor_success = current_hobby.tutor(request.form)

            ##TODO add status messages to user
            if tutor_success:
                message = ""
            else:
                message = ""
            
            return redirect(url_for('account.hobbies'))
    else:
        ##TODO add status messages to user
        message = ""
        return redirect(url_for('hobby.view', hobby_id = hobby_id))
    
@hobby_bp.route('tutor/stop/<hobby_id>', methods=['GET', 'POST'])
def tutor_stop(hobby_id):
    return redirect(url_for('hobby.view', hobby_id = hobby_id))
    
@hobby_bp.route('delete/<hobby_id>', methods=['GET', 'POST'])
def delete(hobby_id):

    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))

    current_hobby = Hobby(hobby_id)
    if request.method == 'GET':
        g.logger.info(f" GET: ------- ACCOUNT/HOBBIES/HOBBY/DELETE/{hobby_id} ------- ")

        if current_hobby.user_id == session.get('user').get("USER_ID"):
            return dr.dynamic_render('pages/hobby/delete.html', hobby=current_hobby.get_json())
        else:
            ##Incase the user manually enters the url to delete a hobby that doesnt belong to them
            message = ""
            session.clear()
            return redirect(url_for('auth.signin'))
        
    if request.method == 'POST':
        g.logger.info(f" GET: ------- ACCOUNT/HOBBIES/HOBBY/DELETE/{hobby_id} ------- ")
        if current_hobby.user_id == session.get('user').get("USER_ID"):
            delete_status = current_hobby.delete()

            if delete_status:
                message = ""
                return redirect(url_for('account.hobbies'))
            else:
                message = ""
                redirect(url_for('hobby.delete', hobby_id = hobby_id))
        else:
            message = ""
            return redirect(url_for('auth.signin'))