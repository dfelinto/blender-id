from flask import Flask
from flask import Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider
from flask.ext.thumbnails import Thumbnail

# Create app
app = Flask(__name__)
import config
app.config.from_object(config.Development)

# Create database connection object
db = SQLAlchemy(app)
mail = Mail(app)
oauth = OAuth2Provider(app)
thumb = Thumbnail(app)

filemanager = Blueprint('filemanager', __name__, static_folder='static/files')

from application.modules.users import model
from application import controller
from application.modules.admin import *
from application.modules.oauth import *
from application.modules.oauth.admin import *

