# STL IMPORTS
from os import environ

# EXT IMPORTS
from flask import Flask, render_template
from waitress import serve

# FLASK INIT
app = Flask(__name__)

print("App Started!")

#########################
##### SERVER ROUTES #####
#########################
@app.route("/", methods=['GET'])
def hello_world():
    print("Someone visited!")
    return render_template("home.html")

#########################
##### SERVER BEGIN! #####
#########################
serve(app, host='0.0.0.0', port=int(environ["APP_PORT"]))