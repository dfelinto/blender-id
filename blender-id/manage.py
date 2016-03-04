
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
def create_blender_id_client():
    """Create OAuth client for the Blender ID authentication."""

    import application.modules.oauth.model as oauth_model

    test_client = oauth_model.Client(
        name='Blender ID custom login',
        description=None,
        picture=None,
        client_id=app.config['BLENDER_ID_LOGIN_CLIENT_ID'],
        client_secret=app.config['BLENDER_ID_LOGIN_CLIENT_SECRET'],
        user_id=None,
        url=None
    )
    db.session.add(test_client)
    db.session.commit()

manager.run()
