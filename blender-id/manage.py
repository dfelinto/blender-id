#!/usr/bin/env python

from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
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

    import application.modules.oauth.model as oauth_model

    oauth_model.create_oauth_clients()
    db.session.commit()


manager.run()
