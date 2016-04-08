from __future__ import print_function

import sys
import logging
import os
import unittest
import datetime

from flask.testing import FlaskClient
import flask_migrate
from flask.ext.migrate import Migrate
import oauthlib.common
import sqlalchemy_utils.functions

MY_PATH = os.path.dirname(os.path.abspath(__file__))


def config_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s %(levelname)8s %(name)s %(message)s')
    logging.getLogger('application').setLevel(logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    logging.getLogger('flask').setLevel(logging.DEBUG)

log = logging.getLogger(__name__)


class AbstractBlenderIdTest(unittest.TestCase):
    def setUp(self):
        config_logging()

        test_config_file = os.path.join(MY_PATH, 'config_testing.py')
        os.environ['BLENDER_ID_CONFIG'] = test_config_file
        log.info('Setting extra config file to %s', test_config_file)

        from application import app

        self.assertTrue(app.config.get('TEST_CONFIGURATION_LOADED'),
                        'Test config file was NOT loaded from %s' % test_config_file)

        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        log.info('Database: %s', db_url)

        if sqlalchemy_utils.functions.database_exists(db_url):
            sqlalchemy_utils.functions.drop_database(db_url)
        sqlalchemy_utils.functions.create_database(db_url)

        # Make sure we have the correct database.
        from application import db

        Migrate(app, db)
        with app.test_request_context():
            migdir = os.path.join(os.path.dirname(MY_PATH), 'blender-id', 'migrations')
            log.info('Loading migrations from %s', migdir)
            flask_migrate.upgrade(directory=migdir)

        # Add the default OAuth clients.
        import application.modules.oauth.model as oauth_model

        oauth_model.create_oauth_clients()
        db.session.commit()
        log.info('Added default OAuth clients.')

        self.db = db
        self.app = app
        self.client = app.test_client()
        assert isinstance(self.client, FlaskClient)

    def tearDown(self):
        del self.client
        del self.app

        to_delete = [modname for modname in sys.modules
                     if modname == 'application' or modname.startswith('application.')]
        for modname in to_delete:
            del sys.modules[modname]

    def create_user(self, **dbfields):
        from application.modules.users.model import user_datastore

        user = user_datastore.create_user(**dbfields)
        return user

    def create_token(self, user_id, client_id, expires_in):
        from application.modules.oauth.model import Token
        from application.modules.users import DEFAULT_OAUTH_TOKEN_SCOPE

        expires = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

        token = Token(
            access_token=oauthlib.common.generate_token(),
            refresh_token=oauthlib.common.generate_token(),
            token_type='Bearer',
            _scopes=DEFAULT_OAUTH_TOKEN_SCOPE,
            expires=expires,
            client_id=client_id,
            user_id=user_id,
            host_label='unittest',
        )
        self.db.session.add(token)
        return token
