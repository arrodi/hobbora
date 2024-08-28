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
@app.route("/", methods=['GET'])
def hello_world():
    print(f"{request.remote_addr} requested!")
    sql_context ="""
    select 
        *
    from 
        customers
    """
    record_str = postgres.execute_query(sql_context)
    return jsonify({"Data":record_str})

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host='0.0.0.0', port=int(settings.app_port))