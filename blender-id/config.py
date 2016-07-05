import os.path

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

DEBUG = False
ASSETS_DEBUG = False  # see https://flask-assets.readthedocs.io/

MAIL_SERVER = '-set-in-local-config-'
MAIL_PORT = 25
MAIL_USE_SSL = True
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
DEFAULT_MAIL_SENDER = 'cloudsupport@blender.org'
SECURITY_EMAIL_SENDER = DEFAULT_MAIL_SENDER

# Flask-Security setup
SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_CONFIRMABLE = True  # Enables confirmation mails.
SECUIRTY_POST_LOGIN = '/'
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = '-set-in-local-config-'
SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED = ('This address already exists', 'error')
SECURITY_LOGIN_USER_TEMPLATE = 'security/login_user.html'
SECURITY_TRACKABLE = True
SECURITY_POST_LOGIN_VIEW = 'homepage'
SECURITY_POST_LOGOUT_VIEW = 'homepage'

SECURITY_MSG_CONFIRMATION_REQUIRED = ('We have enabled an extra check that requires you to '
                                      'confirm your email address.',
                                      'warning')

GOOGLE_ANALYTICS_TRACKING_ID = ''
GOOGLE_ANALYTICS_DOMAIN = ''

# Configure the mount point of the server; usually / but /id on production.
APPLICATION_ROOT = '/'

SESSION_COOKIE_NAME = 'blenderIDsession'

# Token expiry for the username/password (aka special snowflake) authentication system.
OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = 3600 * 24 * 365  # one year, in seconds.
OAUTH2_PROVIDER_ERROR_ENDPOINT = 'oauth_error'

BLENDER_ID_ADDON_CLIENT_ID = '-set-in-local-config-'  # Client ID for the special snowflake client.

DEFAULT_CLIENTS = [
    {
        'name': 'Blender ID addon',
        'id': BLENDER_ID_ADDON_CLIENT_ID,
        'secret': '-set-in-local-config-',
        'redirect_uris': '',
        # no redirect URIs, it uses username/password special snowflake auth.
    },
    {
        'name': 'Blender Cloud',
        'id': '-set-in-local-config-',
        'secret': '-set-in-local-config-',
        'redirect_uris': '-set-in-local-config-',
    },
]

SECRET_KEY = '-set-in-local-config-'
SQLALCHEMY_DATABASE_URI = 'mysql://-set-in-local-config-@mysql/blender_id?charset=utf8'

application_dir = os.path.join(ROOT_PATH, 'application')
MEDIA_FOLDER = os.path.join(application_dir, 'static', 'files')
MEDIA_URL = 'files/'
MEDIA_THUMBNAIL_FOLDER = os.path.join(application_dir, 'static', 'thumbnails')
MEDIA_THUMBNAIL_URL = 'thumbnails/'

CACHE_TYPE = 'null'  # 'filesystem' #null
CACHE_DEFAULT_TIMEOUT = 60
CACHE_DIR = ''

# See https://docs.python.org/2/library/logging.config.html#configuration-dictionary-schema
LOGGING = {
    'version': 1,
    'formatters': {
        'default': {'format': '%(asctime)-15s %(levelname)8s %(name)s %(message)s'}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stderr',
        }
    },
    'loggers': {
        'application': {'level': 'INFO'},
        'werkzeug': {'level': 'INFO'},
    },
    'root': {
        'level': 'WARNING',
        'handlers': [
            'console',
        ],
    }
}

GIT = 'git'
