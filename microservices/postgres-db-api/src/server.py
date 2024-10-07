# STL IMPORTS
from datetime import datetime
import uuid

# EXT IMPORTS
from flask import Flask, jsonify, request
from waitress import serve

# AUTHORED IMPORTS
from scripts.settings import Settings
from scripts.postgres import Postgres
from scripts.queries import Queries

settings = Settings()
postgres = Postgres(settings.db_name, settings.db_user, settings.db_password, settings.db_host, settings.db_port)
queries = Queries()


################################################################################
def prepare_db():
    function_nm = "OVERWRITE_UPD_TS_ON_INSERT"
    function_sql_str = queries.upd_dt_function(function_nm)
    postgres.execute_query(function_sql_str)
    for table_name, column_name in queries.table_schemas.items():
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
print("API INITIALIZED")

#########################
##### SERVER ROUTES #####
#########################

@app.route("/user_accounts/get_user", methods=['POST'])
def get_customer():

    request_data = request.get_json()
    request_email = request_data["USER_EMAIL"]
    sql_context = queries.select_table("USER_ACCOUNTS", queries.table_schemas["USER_ACCOUNTS"].keys(), f"USER_EMAIL = '{request_email}'")
    query_return = list(postgres.execute_query(sql_context, fetch=True))
    
    if query_return:
        query_return = query_return[0]
        # Format datetime fields
        query_return = [value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value for value in query_return]
        
        print(query_return)

        response = {'USER_EXISTS': True}
        for i, key in enumerate(queries.table_schemas["USER_ACCOUNTS"].keys()):
            response[key] = query_return[i]
        return jsonify(response)
    else:
        return jsonify({'USER_EXISTS': False})

@app.route("/user_accounts/add_user", methods=['POST'])
def add_user():

    request_data = request.get_json()
    sql_context = queries.select_table("USER_ACCOUNTS", queries.table_schemas["USER_ACCOUNTS"].keys(), f"USER_NAME = '{request_data["USER_NAME"]}'")
    query_return = postgres.execute_query(sql_context, fetch=True)
    if query_return:
        request_data["INSERT"] = "ERROR"
        request_data["MESSAGE"] = "This username is already in use!"
        return jsonify(request_data)
    else:        
        sql_context = queries.insert_into_table("USER_ACCOUNTS", request_data)
        query_return = postgres.execute_query(sql_context, fetch=False)

    if "QUERY SUCCESS" in query_return:
        request_data["INSERT"] = "SUCCESS"
        request_data["MESSAGE"] = "Succesfully added the user!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["INSERT"] = "ERROR"
        request_data["MESSAGE"] = "This email is already in use! Please login or use another email when signing up."
        return jsonify(request_data)
    else:
        request_data["INSERT"] = "ERROR"
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    
@app.route("/user_accounts/become_tutor", methods=['POST'])
def become_tutor():
    request_data = request.get_json()
    user_email = request_data.pop("USER_EMAIL")
    request_data = {"USER_TUTOR": request_data["USER_TUTOR"]}
    sql_context = queries.modify_record("USER_ACCOUNTS", request_data, f"USER_EMAIL = '{user_email}'")
    query_return = postgres.execute_query(sql_context, fetch=False)
    if "QUERY SUCCESS" in query_return:
        request_data["USER_EMAIL"] = user_email
        request_data["MODIFY"] = "SUCCESS"
        request_data["MESSAGE"] = "Succesfully became a tutor!"
        return jsonify(request_data)
    else:
        request_data["USER_EMAIL"] = user_email
        request_data["MODIFY"] = "FAILURE"
        request_data["MESSAGE"] = "Unknown failure!"
        return jsonify(request_data)

@app.route("/user_hobbies/add_hobby", methods=['POST'])
def add_hobby():

    request_data = request.get_json()
    request_data["HOBBY_ID"] = str(uuid.uuid4().hex[:6])
    request_data["HOBBY_TUTORING"] = False
    sql_context = queries.insert_into_table("USER_HOBBIES", request_data)
    query_return = postgres.execute_query(sql_context, fetch=False)

    if "QUERY SUCCESS" in query_return:
        request_data["INSERT"] = "SUCCESS"
        request_data["MESSAGE"] = "Succesfully added the hobby!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["INSERT"] = "INSERT ERROR"
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["INSERT"] = "UNKOWN ERROR"
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    
@app.route("/user_hobbies/get_hobbies", methods=['POST'])
def get_hobbies():

    request_data = request.get_json()
    request_email = request_data["USER_EMAIL"]
    sql_context = queries.select_table("USER_HOBBIES", queries.table_schemas["USER_HOBBIES"].keys(), f"USER_EMAIL = '{request_email}'")
    query_return = postgres.execute_query(sql_context, fetch=True)

    
    if len(query_return) > 0:
        query_return_lst = []
        for _record in query_return:
            _temp_dict = {}
            for _index, _column in enumerate(queries.table_schemas["USER_HOBBIES"].keys()):
                _temp_dict[_column] = _record[_index]
            query_return_lst.append(_temp_dict)
    else:
        query_return_lst = query_return

    request_data["DATA"] = query_return_lst
    return jsonify(request_data)

@app.route("/user_hobbies/get_hobby", methods=['POST'])
#Returns all information on a single hobby
def get_hobby():

    request_data = request.get_json()
    request_email = request_data["USER_EMAIL"]
    hobby_id = request_data["HOBBY_ID"]
    sql_context = queries.select_table("USER_HOBBIES", queries.table_schemas["USER_HOBBIES"].keys(), f"USER_EMAIL = '{request_email}' AND HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_context, fetch=True)

    
    if query_return:
        query_return_lst = []
        for _record in query_return:
            _temp_dict = {}
            for _index, _column in enumerate(queries.table_schemas["USER_HOBBIES"].keys()):
                _temp_dict[_column] = _record[_index]
            query_return_lst.append(_temp_dict)

    request_data["DATA"] = query_return_lst
    return jsonify(request_data)

@app.route("/user_hobbies/tutor_hobby", methods=['POST'])
def tutor_hobby():

    print("/user_hobbies/tutor_hobby")

    request_data = request.get_json()

    print(request_data)

    hobby_id = request_data["HOBBY_ID"]
    change_data = {"HOBBY_TUTORING":True}
    sql_context = queries.modify_record("USER_HOBBIES", change_data, f"HOBBY_ID = '{hobby_id}'")
    query_return = postgres.execute_query(sql_context, fetch=False)

    print(query_return)
    
    sql_context = queries.insert_into_table("USER_HOBBIES_TUTORING", request_data)
    query_return = postgres.execute_query(sql_context, fetch=False)

    print(query_return)

    if "QUERY SUCCESS" in query_return:
        request_data["INSERT"] = "SUCCESS"
        request_data["MESSAGE"] = "Succesfully added the tutored hobby!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["INSERT"] = "INSERT ERROR"
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["INSERT"] = "UNKOWN ERROR"
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)

@app.route("/user_hobbies/get_tutored_hobbies", methods=['POST'])
#Returns all information on a single hobby
def get_tutored_hobbies():

    request_data = request.get_json()

    USER_HOBBIES_TUTORING_lst = list(queries.table_schemas["USER_HOBBIES_TUTORING"].keys())
    USER_HOBBIES_lst = list(queries.table_schemas["USER_HOBBIES"].keys())

    USER_HOBBIES_TUTORING_lst.extend(USER_HOBBIES_lst)

    for _index, _column in enumerate(USER_HOBBIES_TUTORING_lst):
        if _column in USER_HOBBIES_lst:
            USER_HOBBIES_TUTORING_lst[_index] = f"a.{_column}"

    print("-USER_HOBBIES_COMBINED-")
    print(USER_HOBBIES_TUTORING_lst)

    USER_HOBBIES_COMBINED_SET = set(USER_HOBBIES_TUTORING_lst)

    request_columns = list(USER_HOBBIES_COMBINED_SET)

    sql_context = queries.select_join_table("USER_HOBBIES", "USER_HOBBIES_TUTORING", request_columns, "HOBBY_ID", "HOBBY_TUTORING = true")
    query_return = postgres.execute_query(sql_context, fetch=True)

    request_columns = [_column.replace("a.", "") for _column in request_columns]

    print("/user_hobbies/get_tutored_hobbies")
    print(request_columns)
    print(query_return)

    
    if query_return:
        query_return_lst = []
        for _record in query_return:
            _temp_dict = {}
            for _index, _column in enumerate(request_columns):
                _temp_dict[_column] = _record[_index]
            query_return_lst.append(_temp_dict)

    request_data["DATA"] = query_return_lst
    return jsonify(request_data)
#########################
##### SERVER BEGIN! #####
#########################

serve(app, host=settings.app_host, port=int(settings.app_port))
