# STL IMPORTS
from datetime import datetime
import uuid
import logging

# EXT IMPORTS
from flask import Flask, jsonify, request
from waitress import serve

# AUTHORED IMPORTS
from scripts.settings import Settings
from scripts.postgres import Postgres
from scripts.schemas import Schemas
import scripts.encrypt as encrypt
import scripts.queries as queries

settings = Settings()
postgres = Postgres(settings.db_name, settings.db_user, settings.db_password, settings.db_host, settings.db_port)
schemas = Schemas()

# LOGGING CONFIG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


################################################################################
def prepare_db():
    function_nm = "OVERWRITE_UPD_TS_ON_INSERT"
    function_sql_str = queries.upd_dt_function(function_nm)
    postgres.execute_query(function_sql_str)
    for table_name, column_name in schemas.table_schemas.items():
        create_sql_str = queries.create_table(table_name, column_name)
        postgres.execute_query(create_sql_str)
        if "UPD_DT" in column_name:
            trigger_sql_str = queries.upd_dt_function_trigger(table_name, function_nm)
            postgres.execute_query(trigger_sql_str)

    function_nm = "DEFAULT_TUTOR_MODE_ON_INSERT"
    function_sql_str = queries.tutoring_mode_function(function_nm)
    postgres.execute_query(function_sql_str)
    for table_name in ["USER_HOBBIES_TUTORING"]:
        trigger_sql_str = queries.tutoring_mode_function_trigger(table_name, function_nm)
        postgres.execute_query(trigger_sql_str)
################################################################################

prepare_db()

# FLASK INIT                 
app = Flask(__name__)
print("API HAS BEEN INITIALIZED")

#########################
##### SERVER ROUTES #####
#########################

@app.route("/user/create", methods=['POST'])
def user_create():
    request_data = request.get_json()
    EMAIL = request_data.get("EMAIL")
    USERNAME = request_data.get("USERNAME")

    sql_context = queries.select_table("USER_ACCOUNTS", schemas.table_schemas["USER_ACCOUNTS"].keys(), f"USERNAME = '{USERNAME}'")
    query_return = postgres.execute_query(sql_context, fetch=True)
    logger.info(query_return)

    if query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "This username is already in use!"
        return jsonify(request_data)
    else:
        sql_context = queries.select_table("USER_ACCOUNTS", schemas.table_schemas["USER_ACCOUNTS"].keys(), f"EMAIL = '{EMAIL}'")
        query_return = postgres.execute_query(sql_context, fetch=True)
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
            query_return = postgres.execute_query(sql_query, sql_values, fetch=False)

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

@app.route("/user/authenticate", methods=['POST'])
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
        query_return = list(postgres.execute_query(sql_context, fetch=True))

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

@app.route("/user/get", methods=['POST'])
def user_get():

    try:
    #Get data from the request
        request_data = request.get_json()
        EMAIL = request_data.get("EMAIL")
        USERNAME = request_data.get("USERNAME")
        user_id = request_data.get("USER_ID")

        if EMAIL:
            sql_condition = f"EMAIL = '{EMAIL}'"
        elif USERNAME:
            sql_condition = f"USERNAME = '{USERNAME}'"
        elif user_id:
            sql_condition = f"USER_ID = '{user_id}'"
        else:
            # Log and return a generic error message in case of unexpected issues
            logger.error(f"Error getting user: {str(e)}")
            return jsonify({'error': 'Internal server error.'}), 500 

        sql_context = queries.select_table("USER_ACCOUNTS", schemas.table_schemas["USER_ACCOUNTS"].keys(), sql_condition)
        query_return = list(postgres.execute_query(sql_context, fetch=True))
        
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
    
@app.route("/user/edit", methods=['POST'])
def user_edit():
    request_data = request.get_json()
    user_id = request_data["USER_ID"]
    sql_query, sql_values = queries.modify_record("USER_ACCOUNTS", request_data, f"USER_ID = '{user_id}'")
    query_return = postgres.execute_query(sql_query, sql_values, fetch=False)
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
   
@app.route("/user/tutor/become", methods=['POST'])
def user_tutor_become():
    request_data = request.get_json()
    user_id = request_data["USER_ID"]
    request_data = {"TUTORING": True}
    sql_query, sql_values = queries.modify_record("USER_ACCOUNTS", request_data, f"USER_ID = '{user_id}'")
    query_return = postgres.execute_query(sql_query, sql_values, fetch=False)
    print(query_return)
    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully became a tutor!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "Unknown failure!"
        return jsonify(request_data)
    
@app.route("/user/hobbies/get_ids", methods=['POST'])
def get_hobbies():

    request_data = request.get_json()
    user_id = request_data["USER_ID"]
    sql_context = queries.select_table("USER_HOBBIES", schemas.table_schemas["USER_HOBBIES"].keys(), f"USER_ID = '{user_id}'")
    query_return = postgres.execute_query(sql_context, fetch=True)

    hobby_id_lst = []
    for _record in query_return:
        for _index, _column in enumerate(schemas.table_schemas["USER_HOBBIES"].keys()):
            if _column == "HOBBY_ID":
                hobby_id_lst.append(_record[_index])

    request_data["HOBBY_IDS"] = hobby_id_lst
    return jsonify(request_data)

@app.route("/hobby/add", methods=['POST'])
def hobby_add():
    print("/hobby/add")
    request_data = request.get_json()
    request_data["HOBBY_ID"] = str(uuid.uuid4().hex[:6])
    sql_query, sql_values = queries.insert_into_table("USER_HOBBIES", request_data)
    query_return = postgres.execute_query(sql_query, sql_values, fetch=False)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully added the hobby!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)

@app.route("/hobby/get", methods=['POST'])
def get_hobby():
    print("/hobby/get")
    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_context = queries.select_table("USER_HOBBIES", schemas.table_schemas["USER_HOBBIES"].keys(), f"HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_context, fetch=True)

    print(query_return)

    
    if query_return:
        query_return_lst = []
        for _record in query_return:
            _temp_dict = {}
            for _index, _column in enumerate(schemas.table_schemas["USER_HOBBIES"].keys()):
                _temp_dict[_column] = _record[_index]
            query_return_lst.append(_temp_dict)

        request_data["DATA"] = query_return_lst[0]
    else:
        request_data["DATA"] = {}

    return jsonify(request_data)

@app.route("/hobby/edit", methods=['POST'])
def edit_hobby():
    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_query, sql_values = queries.modify_record("USER_HOBBIES", request_data, f"HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_query, sql_values, fetch=False)
    print(query_return)
    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully edit a hobby!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "Unknown failure!"
        return jsonify(request_data)


@app.route("/hobby/tutor", methods=['POST'])
def hobby_tutor():

    print("/hobby/tutor")

    request_data = request.get_json()

    print(request_data)

    hobby_id = request_data["HOBBY_ID"]
    change_data = {"TUTORING":True}
    sql_query, sql_values = queries.modify_record("USER_HOBBIES", change_data, f"HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_query, sql_values, fetch=False)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully added the tutored hobby!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    
@app.route("/hobby/tutored/get", methods=['POST'])
def get_tutored_hobby():
    print("/hobby/tutored/get")
    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_context = queries.select_table("USER_HOBBIES_TUTORING", schemas.table_schemas["USER_HOBBIES_TUTORING"].keys(), f"HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_context, fetch=True)

    print(query_return)

    if query_return:
        query_return_lst = []
        for _record in query_return:
            _temp_dict = {}
            for _index, _column in enumerate(schemas.table_schemas["USER_HOBBIES_TUTORING"].keys()):
                _temp_dict[_column] = _record[_index]
            query_return_lst.append(_temp_dict)

        request_data["DATA"] = query_return_lst[0]
        request_data["SUCCESS"] = True
        request_data["SELECT"] = len(query_return_lst[0])
    else:
        request_data["SUCCESS"] = True
        request_data["SELECT"] = "EMPTY"
        request_data["DATA"] = {}

    return jsonify(request_data)

@app.route("/hobby/tutored/add", methods=['POST'])
def add_tutored_hobby():
    print("/hobby/tutored/add")

    request_data = request.get_json()

    sql_query, sql_values = queries.insert_into_table("USER_HOBBIES_TUTORING", request_data)
    query_return = postgres.execute_query(sql_query, sql_values)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully added the tutored hobby!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)

@app.route("/hobby/tutored/edit", methods=['POST'])
def edit_tutored_hobby():
    print("/hobby/tutored/edit")
    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_query, sql_values = queries.modify_record("USER_HOBBIES_TUTORING", request_data, f"HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_query, sql_values)
    print(query_return)
    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully edited a hobby!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = "Unknown failure!"
        return jsonify(request_data)
    
@app.route("/hobby/delete", methods=['POST'])
def delete_hobby():
    print("/hobby/delete")

    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_query, sql_values = queries.delete_record("USER_HOBBIES", f"HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_query)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully deleted the hobby!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    
@app.route("/hobby/tutored/delete", methods=['POST'])
def delete_tutored_hobby():
    print("/hobby/tutored/delete")

    request_data = request.get_json()
    hobby_id = request_data["HOBBY_ID"]

    sql_query, sql_values = queries.delete_record("USER_HOBBIES_TUTORING", f"HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_query)

    if "QUERY SUCCESS" in query_return:
        request_data["SUCCESS"] = True
        request_data["MESSAGE"] = "Succesfully deleted the hobby!"
        return jsonify(request_data)
    else:
        request_data["SUCCESS"] = False
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)

@app.route("/catalog/hobbies/get", methods=['GET'])
#Returns all information on a single hobby
def catalog_hobbies_get():
    print("/catalog/hobbies/get")
    try: 
        where_clause_string = ""
        for key in ['type', 'experience_years', 'proficiency', 'hourly_rate', 'mode_live_call', 'mode_public_in_person', 'mode_private_in_person']:
            value = request.args.get(key)
            if value is not None:
                if where_clause_string:  # Add a comma separator if the string already has content
                    where_clause_string += " AND "
                key = key.upper()
                if key in list(schemas.table_schemas["USER_HOBBIES_TUTORING"].keys()):
                    if "text" in schemas.table_schemas["USER_HOBBIES_TUTORING"][key]:
                        where_clause_string += f"{key}='{value}'"
                    else:
                        where_clause_string += f'{key}={value}'
                if key in list(schemas.table_schemas["USER_HOBBIES"].keys()):
                    if "text" in schemas.table_schemas["USER_HOBBIES"][key]:
                        where_clause_string += f"{key} = '{value}'"
                    else:
                        where_clause_string += f"{key} = {value}"

        if where_clause_string:
            where_clause_string = "TUTORING = true AND " + where_clause_string
        else:
            where_clause_string = "TUTORING = true"

        USER_HOBBIES_TUTORING_lst = list(schemas.table_schemas["USER_HOBBIES_TUTORING"].keys())
        USER_HOBBIES_lst = list(schemas.table_schemas["USER_HOBBIES"].keys())

        USER_HOBBIES_TUTORING_lst.extend(USER_HOBBIES_lst)

        for _index, _column in enumerate(USER_HOBBIES_TUTORING_lst):
            if _column in USER_HOBBIES_lst:
                USER_HOBBIES_TUTORING_lst[_index] = f"a.{_column}"

        USER_HOBBIES_COMBINED_SET = set(USER_HOBBIES_TUTORING_lst)

        request_columns = list(USER_HOBBIES_COMBINED_SET)

        sql_query = queries.select_join_table("USER_HOBBIES", "USER_HOBBIES_TUTORING", request_columns, "HOBBY_ID", where_clause_string)
        
        query_return = postgres.execute_query(sql_query, fetch=True)
        

        request_columns = [_column.replace("a.", "") for _column in request_columns]

        return_data = {}
        if query_return:
            query_return_lst = []
            for _record in query_return:
                _temp_dict = {}
                for _index, _column in enumerate(request_columns):
                    _temp_dict[_column] = _record[_index]
                query_return_lst.append(_temp_dict)
            
            return_data["SUCCESS"] = True
            return_data["MESSAGE"] = "Pulled: " + str(len(query_return_lst)) + " number of records."
            return_data["DATA"] = query_return_lst
        else:
            return_data["SUCCESS"] = True
            return_data["MESSAGE"] = "Query returned no results."
            return_data["DATA"] = []
        return jsonify(return_data)

    #TODO fix this error handling
    except FileNotFoundError as e:
        return_data["SUCCESS"] = False
        return_data["MESSAGE"] = str(e)
        return_data["DATA"] = []
        return jsonify(return_data)

#########################
##### SERVER BEGIN! #####
#########################

serve(app, host=settings.app_host, port=int(settings.app_port))
