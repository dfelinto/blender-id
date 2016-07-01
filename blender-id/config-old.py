class Config(object):
    # Configured for GMAIL
    MAIL_SERVER = 'smtp.stuvel.eu'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    DEFAULT_MAIL_SENDER = 'cloudsupport@blender.org'

    # Flask-Security setup
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_CONFIRMABLE = False
    SECUIRTY_POST_LOGIN = '/'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = '/2aX16zPnnIgfMwkOjGX4S'
    SECURITY_EMAIL_SENDER = 'cloudsupport@blender.org'
    SECURITY_POST_REGISTER_VIEW = '/id'
    SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED = ('This address already exists', 'error')
    GOOGLE_ANALYTICS_TRACKING_ID = ''
    GOOGLE_ANALYTICS_DOMAIN = ''
    SECURITY_TRACKABLE = True

    # Token expiry for the username/password (aka special snowflake) authentication system.
    OAUTH2_PROVIDER_TOKEN_EXPIRES_IN = 3600 * 24 * 365  # one year, in seconds.
    BLENDER_ID_ADDON_CLIENT_ID = 'SPECIAL-SNOWFLAKE-57'  # Client ID for the special snowflake client.

    DEFAULT_CLIENTS = [
        {
            'name': 'Blender ID addon',
            'id': BLENDER_ID_ADDON_CLIENT_ID,
            'secret': 'oQuawiephohl5yeeM2Faiv8Ozaengii7',
            'redirect_uris': '',
        # no redirect URIs, it uses username/password special snowflake auth.
        },
        {
            'name': 'Blender Cloud',
            'id': 'CLOUD-OF-SNOWFLAKES-42',
            'secret': 'thohghoh5XeisodoThaateewo2chooy3',
            'redirect_uris': 'http://pillar_web:5001/oauth/blender-id/authorized',
        },
    ]


class Development(Config):
    application_dir = '/data/git/blender-id/application'
    SECRET_KEY = ':o{\x1cR?\xd7\xc3I\xd1\xdca\xb5\x15\xd4\xc0\x8e\x1b\xad\x18P\x93\x17\x1d'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@mysql/blender_id?charset=utf8'
    SECURITY_REGISTERABLE = True
    SECURITY_LOGIN_USER_TEMPLATE = 'security/login_user.html'
    MEDIA_FOLDER = application_dir + '/static/files'
    MEDIA_URL = 'files/'
    MEDIA_THUMBNAIL_FOLDER = application_dir + '/static/thumbnails'
    MEDIA_THUMBNAIL_URL = 'thumbnails/'
    ASSETS_DEBUG = False
    CACHE_TYPE = 'null'  # 'filesystem' #null
    CACHE_DEFAULT_TIMEOUT = 60
    CACHE_DIR = '/Users/fsiddi/Developer/blender-cloud/server/cache/'
