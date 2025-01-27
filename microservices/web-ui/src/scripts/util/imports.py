import os
import uuid
import base64
import json
import logging
from datetime import timedelta
from io import BytesIO

# EXT IMPORTS
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Blueprint, g
from waitress import serve

# AUTHORED IMPORTS
from scripts.util.settings import Settings
from scripts.objects.user import User
from scripts.objects.hobby import Hobby
from scripts.util import dynamic_render as dr

