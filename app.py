from flask import Flask
from flask_cors import CORS, cross_origin
from flask_uuid import FlaskUUID

app = Flask(__name__)
FlaskUUID(app)
CORS(app)