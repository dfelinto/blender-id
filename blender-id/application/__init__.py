import os
import logging

from flask import Flask
from flask import Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask_oauthlib.provider import OAuth2Provider
from flask.ext.thumbnails import Thumbnail
from flask.ext.security import Security

# Create app
app = Flask(__name__)
import config
app.config.from_object(config.Development)

if 'BLENDER_ID_CONFIG' in os.environ:
    app.config.from_pyfile(os.environ['BLENDER_ID_CONFIG'], silent=False)

# Configure logging
logging.basicConfig(level=logging.DEBUG if app.config['DEBUG'] else logging.INFO)
log = logging.getLogger(__name__)

# Create database connection object
db = SQLAlchemy(app)
mail = Mail(app)
oauth = OAuth2Provider(app)
thumb = Thumbnail(app)

filemanager = Blueprint('filemanager', __name__, static_folder='static/files')

if 'BUGSNAG_API_KEY' in app.config:
    import bugsnag
    from bugsnag.flask import handle_exceptions
    bugsnag.configure(
        api_key = app.config['BUGSNAG_API_KEY'],
        project_root = app.config['APPLICATION_ROOT']
    )
    handle_exceptions(app)

from application.modules.users import model
from application.modules.users.forms import ExtendedRegisterForm
security = Security(app, model.user_datastore,
         register_form=ExtendedRegisterForm)

from application.modules.users import *
from application import controller
from application.modules.admin import *
from application.modules.oauth import *
from application.modules.oauth.admin import *
from application.modules import subclients

app.register_blueprint(oauth_api, url_prefix='/api')
app.register_blueprint(subclients.subclients, url_prefix='/subclients')
