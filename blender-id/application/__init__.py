from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from werkzeug.security import gen_salt
from flask_oauthlib.provider import OAuth2Provider

# Create app
app = Flask(__name__)
import config
app.config.from_object(config.Development)

# Create database connection object
db = SQLAlchemy(app)

mail = Mail(app)

oauth = OAuth2Provider(app)

from application.modules.users import model
from application import controller
from application.modules.admin import *
from application.modules.oauth import *
