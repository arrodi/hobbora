# STL IMPORTS
from os import environ
import json

# EXT IMPORTS
from flask import Flask, jsonify, request
from waitress import serve

#AUTHORED IMPORTS
from scripts.settings import Settings
from scripts.postgres import Postgres

settings = Settings()
postgres = Postgres(settings.db_name, settings.db_user, settings.db_password, settings.db_host, settings.db_port)

# FLASK INIT
app = Flask(__name__)
print("API INITIALIZED")
#########################
##### SERVER ROUTES #####
#########################
@app.route("/", methods=['GET'])
def health_check():
    response_dict = postgres.test_connection()

    return jsonify(response_dict)

@app.route("/user_accounts", methods=['GET'])
def list_customers():
    sql_context =f"""
    SELECT 
        USER_ID, USER_NAME
    FROM 
        USER_ACCOUNTS
    """

    print(sql_context)

    users_str = postgres.execute_query(sql_context, True)

    return_lst = []

    for pair in users_str:
        return_dict = {}
        return_dict["USER_ID"] = pair[0]
        return_dict["USER_NAME"] = pair[1]
        return_lst.append(return_dict)

    return jsonify(return_lst)

@app.route("/user_accounts/get_password", methods=['GET'])
def get_customer():
    print(f"{request.remote_addr} requested!")

    username_param = request.args.get('username')

    sql_context =f"""
    SELECT 
        USER_PASS
    FROM 
        USER_ACCOUNTS
    WHERE
        USER_NAME='{username_param}'
    """

    print(sql_context)

    password_str = postgres.execute_query(sql_context, True)

    if password_str:

        if isinstance(password_str, list):
            password_str = password_str[0][0]

        response = {
        'username': username_param,
        'password': password_str,
        'message': 'GET request received successfully!'
        }

    else:
        response = {
        'username': username_param,
        'password': "",
        'message': 'GET request received successfully!'
        }

    return jsonify(response)

@app.route("/user_accounts/add_user", methods=['POST'])
def add_user():
    request_data = json.loads(request.get_json())

    print(request_data)
    print(type(request_data))

    column_lst = []
    value_lst = []
    for _key, _item in request_data.items():
        column_lst.append(_key)
        value_lst.append(f"'{_item}'")

    column_lst_str = ", ".join(column_lst)
    value_lst_str = ", ".join(value_lst)

    sql_context =f"""
    INSERT INTO
        USER_ACCOUNTS ({column_lst_str})
        VALUES ({value_lst_str});
    """

    print(sql_context)

    postgres.execute_query(sql_context)

    request_data["insert"] = "success"

    return jsonify(request_data)

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host=settings.app_host, port=int(settings.app_port))