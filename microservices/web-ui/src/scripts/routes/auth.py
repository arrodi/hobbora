from scripts.util.imports import *

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/sign-in", methods=['GET', 'POST'])
def signin():
    g.logger.info(" ------- SIGN-IN ------- ")
    
    if session.get('user'):
        g.logger.info("User already signed in. Redirecting to the home page.")
        return redirect(url_for('home_page'))
    
    if request.method == 'GET':
        g.logger.info("Rendering sign-in page.")
        return dr.dynamic_render("pages/auth/signin.html")
    
    if request.method == 'POST':
        g.logger.info("Sign-in form submitted.")
        user_input_id = request.form['USER_INPUT']
        user_input_pass = request.form['PASSWORD']

        if len(user_input_id.split(".")) > 1:
            auth_check = User.authenticate(user_input_pass, email = user_input_id)
        else:
            auth_check = User.authenticate(user_input_pass, username = user_input_id)

        if auth_check["USER_EXISTS"]:
            if auth_check["USER_AUTHENTICATED"]:
                g.logger.info(f"Password verified for: {user_input_id}. Setting session.")
                if len(user_input_id.split(".")) > 1:
                    g.current_user = User(email = user_input_id)
                else:
                    g.current_user = User(username = user_input_id)
                session["user"] = g.current_user.get_json()
                session.modified = True
                return redirect(url_for('account.profile'))
            else:
                g.logger.warning(f"Password mismatch for: {user_input_id}")
                error_message = "Incorrect password. Please try again!"
        else:
            g.logger.warning(f"No user found for: {user_input_id}")
            error_message = "No Email Found! Try Again or Sign Up!"

        g.logger.info("Rendering sign-in page with error message.")
        return dr.dynamic_render("pages/auth/signin.html", error_message=error_message)

    
@auth_bp.route("/sign-up", methods=['GET', 'POST'])
def signup():
    if session.get('user'):
        return redirect(url_for('home_page'))
    
    if request.method == 'GET':
        return dr.dynamic_render("pages/auth/signup.html")
    
    if request.method == 'POST':
        create_response = User.create(request.form["USERNAME"], request.form["EMAIL"], request.form["PASSWORD"])
        
        if create_response["SUCCESS"]:
            g.current_user = User(username = request.form["USERNAME"])
            session["user"] = g.current_user.get_json()
            session.modified = True
            return redirect(url_for('home_page'))
        else:
            error_message = create_response.get("MESSAGE", "Unknown error. Please try again!")
            return dr.dynamic_render("pages/auth/signup.html", error_message=error_message)
        
@auth_bp.route('/log-out')
def logout():
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))
    else:
        g.current_user.__del__()
        session.clear()
        success_message = "You have been succesfully logged out."
        g.logger.warning(success_message)
        return redirect(url_for('home_page', success_message=success_message))