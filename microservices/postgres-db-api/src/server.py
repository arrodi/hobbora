# STL IMPORTS
from datetime import datetime

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

def prepare_db():
    function_nm = "OVERWRITE_UPD_TS_ON_INSERT"
    function_sql_str = queries.table_function(function_nm)
    postgres.execute_query(function_sql_str)
    for table_name, column_name in queries.table_schemas.items():
        create_sql_str = queries.create_table(table_name, column_name)
        postgres.execute_query(create_sql_str)
        if "UPD_DT" in column_name:
            trigger_sql_str = queries.function_trigger(table_name, function_nm)
            postgres.execute_query(trigger_sql_str)

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
    sql_context = queries.select_table("USER_ACCOUNTS", queries.table_schemas["USER_ACCOUNTS"].keys(), f"USER_EMAIL = '{request_data["USER_EMAIL"]}'")
    query_return = list(postgres.execute_query(sql_context, fetch=True))
    
    if query_return:
        query_return = query_return[0]
        # Format datetime fields
        query_return = [value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value for value in query_return]
        
        response = {'USER_EXISTS': True}
        for i, key in enumerate(queries.table_schemas["USER_ACCOUNTS"].keys()):
            response[key] = query_return[i]
        return jsonify(response)
    else:
        return jsonify({'USER_EXISTS': False})

@app.route("/user_accounts/add_user", methods=['POST'])
def add_user():

    request_data = request.get_json()
    sql_context = queries.insert_into_table("USER_ACCOUNTS", request_data)
    query_return = postgres.execute_query(sql_context, fetch=False)

    if "QUERY SUCCESS" in query_return:
        request_data["INSERT"] = "SUCCESS"
        request_data["MESSAGE"] = "Succesfully added the user!"
        return jsonify(request_data)
    elif "INSERT ERROR" in query_return:
        request_data["INSERT"] = "INSERT ERROR"
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    else:
        request_data["INSERT"] = "UNKOWN ERROR"
        request_data["MESSAGE"] = query_return
        return jsonify(request_data)
    

@app.route("/user_hobbies/add_hobby", methods=['POST'])
def add_hobby():

    request_data = request.get_json()
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
    sql_context = queries.select_table("USER_HOBBIES", queries.table_schemas["USER_HOBBIES"].keys(), f"USER_EMAIL = '{request_data["USER_EMAIL"]}'")
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
#########################
##### SERVER BEGIN! #####
#########################

serve(app, host=settings.app_host, port=int(settings.app_port))
