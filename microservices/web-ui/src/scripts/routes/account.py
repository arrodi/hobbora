from scripts.util.imports import *

account_bp = Blueprint('account', __name__)

@account_bp.route("", methods=['GET'])
def account():
    return redirect(url_for('account.profile'))
    
@account_bp.route("/profile", methods=['GET'])
def profile():
    success_message = request.args.get('success_message')
    error_message = request.args.get('error_message')
    g.logger.info(" ------- ACCOUNT/PROFILE ------- ")
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))
    else:
        return dr.dynamic_render("pages/account/profile/profile.html", success_message=success_message, error_message=error_message)
    
@account_bp.route("/profile/edit/picture", methods=['GET', 'POST'])
def profile_edit_picture():
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))
    
    if request.method == 'GET':
        return dr.dynamic_render("pages/account/profile/edit/picture.html")

    if request.method == 'POST':
        file = request.files['file']
        files = {'file': (file.filename, file.stream, file.content_type)}
        upload_status = g.current_user.upload_profile_picture(files)
        
        if upload_status:
            return redirect(url_for('account.profile'))
        else:
            return redirect(url_for('account.profile_edit_picture'))
    
@account_bp.route("/profile/edit/description", methods=['GET', 'POST'])
def profile_edit_description():

    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))
    
    if request.method == 'GET':
        return dr.dynamic_render("pages/account/profile/edit/description.html")
    
    if request.method == 'POST':
        
        edit_user_return = g.current_user.edit(request.form.to_dict())
        if edit_user_return["SUCCESS"]:
            session["user"] = g.current_user.get_json()
            session.modified = True
            return redirect(url_for('account.profile'))
        else:
            error_message = "Error updating user description!"
            return dr.dynamic_render("pages/account/profile/edit/description.html", error_message = error_message)

@account_bp.route('/become-tutor', methods=['GET', 'POST'])
def become_tutor():
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin')) 

    if session.get('user').get("TUTORING"):
        return redirect(url_for('account.profile'))

    if request.method == 'GET':
        return redirect(url_for('account.user_agreement'))

    if request.method == 'POST':
        return redirect(url_for('account.profile'))
    
@account_bp.route('/become-tutor/user_agreement', methods=['GET', 'POST'])
def user_agreement():
    success_message = request.args.get('success_message')
    error_message = request.args.get('error_message')
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))
    
    if request.method == 'GET':
        return dr.dynamic_render('pages/account/profile/user_agreement.html', error_message=error_message)
    
    if request.method == 'POST':
        become_tutor_return = g.current_user.become_tutor()
        session["user"] = g.current_user.get_json()
        session.modified = True

        if become_tutor_return["SUCCESS"]:
            success_message = "You have succesfully became a tutor!"
            return redirect(url_for('account.profile', success_message=success_message))
        else:
            error_message = "Not able to become a tutor!"
            return redirect(url_for('account.become_tutor', error_message=error_message))
    
@account_bp.route("/hobbies", methods=['GET'])
def hobbies():
    g.logger.info(" ------- ACCOUNT/HOBBIES ------- ")
    success_message = request.args.get('success_message')
    error_message = request.args.get('error_message')
    
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))
    
    try:
        hobby_data = []
        for _hobby_id in g.current_user.get_hobby_ids():
            current_hobby = Hobby(_hobby_id)
            hobby_dict = current_hobby.get_json()
            try:
                hobby_dict.update(current_hobby.get_pictures())
                hobby_data.append(hobby_dict)
            except Exception as e:
                g.logger.exception(f"Error occurred while fetching pictures for hobby {current_hobby.id}: {str(e)}")
        
        g.logger.info("Successfully fetched hobbies data with pictures.")

        return dr.dynamic_render("pages/account/hobbies.html", hobbies=hobby_data, user=g.current_user.get_json(), success_message=success_message, error_message=error_message)
    except Exception as e:
        error_message = "An error occurred while fetching hobbies data!"
        g.logger.exception(f"{error_message}: {str(e)}")
        return redirect(url_for('account.profile', error_message=error_message))
    
@account_bp.route("/sessions", methods=['GET'])
def sessions():
    return redirect(url_for('account.profile'))

@account_bp.route("/payments", methods=['GET'])
def payments():
    return redirect(url_for('account.profile'))