from scripts.util.imports import *

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route("", methods=['GET', 'POST'])
def catalog():
    
    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))
    

    if request.method == 'GET':
        g.logger.info(" GET: ------- CATALOG ------- ")
        dict_payload = None
    
    if request.method == 'POST':
        g.logger.info(" POST: ------- CATALOG ------- ")
        dict_payload = dict(request.form)
        dict_payload["USER_ID"] = g.current_user.id
        print(dict_payload)

    try:
        hobby_data = []
        for _hobby in Hobby.get_all(dict_payload):
            current_hobby = Hobby(_hobby["HOBBY_ID"])
            hobby_dict = current_hobby.get_json()
            try:
                hobby_dict.update(current_hobby.get_pictures())
                hobby_data.append(hobby_dict)
            except Exception as e:
                g.logger.exception(f"Error occurred while fetching pictures for hobby {current_hobby.id}: {str(e)}")
        
        g.logger.info("Successfully fetched hobbies data with pictures.")

        return dr.dynamic_render("pages/catalog/catalog.html", hobbies=hobby_data, input=dict_payload)
    except Exception as e:
        g.logger.exception(f"An error occurred while fetching hobbies data: {str(e)}")
        return redirect(url_for('account.profile'))

@catalog_bp.route("hobby/view/<hobby_id>'", methods=['GET'])
def hobby_view(hobby_id):
    g.logger.info(f" ------- CATALOG/HOBBY/VIEW/{hobby_id} ------- ")

    if not session.get('user'):
        g.logger.warning("User session not found. Redirecting to sign-in page.")
        return redirect(url_for('auth.signin'))

    if request.method == 'GET':
        current_hobby = Hobby(hobby_id)
        hobby_data = current_hobby.get_json()
        hobby_data.update(current_hobby.get_pictures())
        hobby_owner = User(id = current_hobby.user_id)
        hobby_data["user"] = hobby_owner.get_json()
        hobby_data["user"]["PROFILE_PICTURE"] = hobby_owner.get_profile_picture()
        del hobby_owner

    return dr.dynamic_render('pages/catalog/hobby/view.html', hobby=hobby_data, user=g.current_user.get_json())