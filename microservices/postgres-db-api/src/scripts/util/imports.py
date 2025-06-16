from datetime import datetime
import uuid
import logging

# EXT IMPORTS
from flask import Flask, jsonify, request
from waitress import serve

# AUTHORED IMPORTS
from util.settings import Settings
from util.postgres import Postgres
from util.schemas import Schemas
import util.encrypt as encrypt
import util.queries as queries