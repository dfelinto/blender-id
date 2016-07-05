import os
import logging.config
import subprocess

from flask import Flask
from flask import Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask_oauthlib.provider import OAuth2Provider
from flask.ext.thumbnails import Thumbnail
from flask.ext.security import Security

# Create app
app = Flask(__name__)

# Load configuration from three different sources, to make it easy to override
# settings with secrets, as well as for development & testing.
app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config.from_pyfile(os.path.join(app_root, 'config.py'), silent=False)
app.config.from_pyfile(os.path.join(app_root, 'config_local.py'), silent=True)
from_envvar = os.environ.get('BLENDER_ID_CONFIG')
if from_envvar:
    # Don't use from_envvar, as we want different behaviour. If the envvar
    # is not set, it's fine (i.e. silent=True), but if it is set and the
    # configfile doesn't exist, it should error out (i.e. silent=False).
    app.config.from_pyfile(from_envvar, silent=False)

# Configure logging
logging.config.dictConfig(app.config['LOGGING'])
log = logging.getLogger(__name__)
if app.config['DEBUG']:
    log.info('BlenderID starting, debug=%s', app.config['DEBUG'])

# Get the Git hash
try:
    git_cmd = [app.config['GIT'], '-C', app_root, 'describe', '--always']
    description = subprocess.check_output(git_cmd)
    app.config['GIT_REVISION'] = description.strip()
except (subprocess.CalledProcessError, OSError) as ex:
    log.warning('Unable to run "git describe" to get git revision: %s', ex)
    app.config['GIT_REVISION'] = 'unknown'
log.info('Git revision %r', app.config['GIT_REVISION'])


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
        project_root = app.config['APPLICATION_ROOT'],
        revision=app.config['GIT_REVISION'],
    )
    handle_exceptions(app)

from application.modules.users import model, forms
security = Security(app, model.user_datastore,
                    register_form=forms.ExtendedRegisterForm,
                    confirm_register_form=forms.ExtendedRegisterForm,
                    login_form=forms.NicerLoginForm)

from application.modules.users import *
from application import controller
from application.modules.admin import *
from application.modules.oauth import *
from application.modules.oauth.admin import *
from application.modules import subclients

app.register_blueprint(oauth_api, url_prefix='/api')
app.register_blueprint(subclients.subclients, url_prefix='/subclients')
