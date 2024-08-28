# STL IMPORTS
from os import environ

# EXT IMPORTS
from flask import Flask, jsonify, request
from waitress import serve

#AUTHORED IMPORTS
from scripts.settings import Settings
from scripts.postgres import Postgres

print("App Started!")

settings = Settings()
postgres = Postgres(settings.db_name, settings.db_user, settings.db_password, settings.db_host, settings.db_port)

# FLASK INIT
app = Flask(__name__)

#########################
##### SERVER ROUTES #####
#########################
@app.route("/get_password", methods=['GET'])
def get_customer():
    print(f"{request.remote_addr} requested!")

    username_param = request.args.get('username')

    sql_context =f"""
    SELECT 
        PASSWORD
    FROM 
        USER_ACCOUNTS
    WHERE
        USERNAME='{username_param}'
    """

    print(sql_context)

    password_str = postgres.execute_query(sql_context)

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

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host='0.0.0.0', port=int(settings.app_port))