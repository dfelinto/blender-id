#!/usr/bin/env python

from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask.ext.migrate import MigrateCommand
from application import app
from application import db

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def create_all_tables():
    """Creates all tables based on imported db models
    """
    db.create_all()

@manager.command
def runserver():
    """Overrides the default runserver from flask-script
    """
    app.run(debug=True, port=8000, host='0.0.0.0')


@manager.command
def create_oauth_clients():
    """Creates the default OAuth clients from config.py.

     Default clients that already exist in the database will be removed and re-added.
     """

    for client_config in app.config['DEFAULT_CLIENTS']:
        _create_oauth_client(client_config)

    db.session.commit()


def _create_oauth_client(client_config):
    """Creates an OAuth client in the database."""

    import application.modules.oauth.model as oauth_model
    # Make sure the client only exists once
    client = oauth_model.Client.query.filter_by(client_id=client_config['id']).first()
    if client is not None:
        print('Removing pre-existing client %r from database' % client_config['name'])
        db.session.delete(client)
    test_client = oauth_model.Client(
        name=client_config['name'],
        description=None,
        picture=None,
        client_id=client_config['id'],
        client_secret=client_config['secret'],
        user_id=None,
        url=None,
        _default_scopes='email',
        _redirect_uris=client_config['redirect_uris'],
    )
    print('Adding new client %r to database' % client_config['name'])
    db.session.add(test_client)


manager.run()
