# routes/user_routes.py
from flask import Blueprint, request, jsonify, current_app
import uuid
import logging
from scripts.util.imports import *

user_bp = Blueprint("user", __name__)
logger = logging.getLogger(__name__)

@user_bp.route("/create", methods=['POST'])
def user_create():
    request_data = request.get_json()
    EMAIL = request_data.get("EMAIL")
    USERNAME = request_data.get("USERNAME")

    sql_context = queries.select_table("USER_ACCOUNTS", schemas.table_schemas["USER_ACCOUNTS"].keys(), f"USERNAME = '{USERNAME}'")
    query_return = g.postgres.execute_query(sql_context, fetch=True)
    logger.info(query_return)

    if query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "This username is already in use!"
        return jsonify(request_data)
    else:
        sql_context = queries.select_table("USER_ACCOUNTS", schemas.table_schemas["USER_ACCOUNTS"].keys(), f"EMAIL = '{EMAIL}'")
        query_return = g.postgres.execute_query(sql_context, fetch=True)
        if query_return:
            request_data["SUCCESS"] = False
            request_data["MESSAGE"] = "This email is already in use!"
            return jsonify(request_data)
        else:
            request_data["USER_ID"] = str(uuid.uuid4().hex[:6])
            request_data["PASSWORD"] = encrypt.hash_password(request_data["PASSWORD"]),
            request_data["TUTORING"] = False
            print(request_data)
            sql_query, sql_values = queries.insert_into_table("USER_ACCOUNTS", request_data)
            query_return = g.postgres.execute_query(sql_query, sql_values, fetch=False)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully added the user!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "This email is already in use! Please login or use another email when signing up."
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)

@user_bp.route("/authenticate", methods=['POST'])
def user_authenticate():
    try:
        #Get data from the request
        request_data = request.get_json()
        EMAIL = request_data.get("EMAIL")
        USERNAME = request_data.get("USERNAME")
        input_password = request_data.get("PASSWORD")

        if EMAIL:
            sql_condition = f"EMAIL = '{EMAIL}'"
        elif USERNAME:
            sql_condition = f"USERNAME = '{USERNAME}'"
        else:
            # Log and return a generic error message in case of unexpected issues
            logger.error(f"Error getting user: {str(e)}")
            return jsonify({'error': 'Internal server error.'}), 500 

        sql_context = queries.select_table("USER_ACCOUNTS", schemas.table_schemas["USER_ACCOUNTS"].keys(), sql_condition)
        query_return = list(g.postgres.execute_query(sql_context, fetch=True))

        print(query_return)

        # Check if user exists and validate password
        if query_return:
            query_return = query_return[0]
            for i, key in enumerate(schemas.table_schemas["USER_ACCOUNTS"].keys()):
                if key == "PASSWORD":
                    
                    if encrypt.check_password(input_password, query_return[i]):
                        return jsonify({'USER_EXISTS': True, 'USER_AUTHENTICATED': True})

                    # Password mismatch
                    return jsonify({'USER_EXISTS': True, 'USER_AUTHENTICATED': False})

        # User doesn't exist
        return jsonify({'USER_EXISTS': False, 'USER_AUTHENTICATED': False})

    except Exception as e:
        # Log and return a generic error message in case of unexpected issues
        logger.error(f"Error authenticating user: {str(e)}")
        return jsonify({'error': 'Internal server error.'}), 500 

@user_bp.route("/get", methods=['POST'])
def user_get():
    print("/user/get")

    try:
    #Get data from the request
        request_data = request.get_json()
        email = request_data.get("EMAIL")
        username = request_data.get("USERNAME")
        user_id = request_data.get("USER_ID")

        if email:
            sql_condition = f"EMAIL = '{email}'"
        elif username:
            sql_condition = f"USERNAME = '{username}'"
        elif user_id:
            sql_condition = f"USER_ID = '{user_id}'"
        else:
            # Log and return a generic error message in case of unexpected issues
            logger.error(f"Error getting user: {str(e)}")
            return jsonify({'error': 'Internal server error.'}), 500 

        sql_context = queries.select_table("USER_ACCOUNTS", schemas.table_schemas["USER_ACCOUNTS"].keys(), sql_condition)
        query_return = list(g.postgres.execute_query(sql_context, fetch=True))
        
        if query_return:
            query_return = query_return[0]
            # Format datetime fields
            query_return = [value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value for value in query_return]
            
            print(query_return)

            response = {'USER_EXISTS': True, 'DATA': request_data}
            for i, key in enumerate(schemas.table_schemas["USER_ACCOUNTS"].keys()):
                response['DATA'][key] = query_return[i]
            return jsonify(response)
        else:
            return jsonify({'USER_EXISTS': False})
    except Exception as e:
        # Log and return a generic error message in case of unexpected issues
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({'error': 'Internal server error.'}), 500 
    
@user_bp.route("/edit", methods=['POST'])
def user_edit():
    request_data = request.get_json()
    user_id = request_data["USER_ID"]
    sql_query, sql_values = queries.modify_record("USER_ACCOUNTS", request_data, f"USER_ID = '{user_id}'")
    query_return = g.postgres.execute_query(sql_query, sql_values, fetch=False)
    print(query_return)
    if "QUERY SUCCESS" in query_return:
        request_data["USER_ID"] = user_id
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully edit an account!"
        return jsonify(request_data)
    else:
        request_data["USER_ID"] = user_id
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "Unknown failure!"
        return jsonify(request_data)
   
@user_bp.route("/user/tutor/become", methods=['POST'])
def user_tutor_become():
    request_data = request.get_json()
    user_id = request_data["USER_ID"]
    request_data = {"TUTORING": True}
    sql_query, sql_values = queries.modify_record("USER_ACCOUNTS", request_data, f"USER_ID = '{user_id}'")
    query_return = g.postgres.execute_query(sql_query, sql_values, fetch=False)
    print(query_return)
    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully became a tutor!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "Unknown failure!"
        return jsonify(request_data)
    
@user_bp.route("/hobbies/get_ids", methods=['POST'])
def get_hobbies():

    request_data = request.get_json()
    user_id = request_data["USER_ID"]
    sql_context = queries.select_table("USER_HOBBIES", schemas.table_schemas["USER_HOBBIES"].keys(), f"USER_ID = '{user_id}'")
    query_return = g.postgres.execute_query(sql_context, fetch=True)

    hobby_id_lst = []
    for _record in query_return:
        for _index, _column in enumerate(schemas.table_schemas["USER_HOBBIES"].keys()):
            if _column == "HOBBY_ID":
                hobby_id_lst.append(_record[_index])

    request_data["HOBBY_IDS"] = hobby_id_lst
    return jsonify(request_data)