
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

    # Make sure the client only exists once
    client = oauth_model.Client.query.filter_by(client_id=app.config['BLENDER_ID_LOGIN_CLIENT_ID']).first()
    if client is not None:
        print('Removing pre-existing client from database')
        db.session.delete(client)

    test_client = oauth_model.Client(
        name='Blender ID custom login',
        description=None,
        picture=None,
        client_id=app.config['BLENDER_ID_LOGIN_CLIENT_ID'],
        client_secret=app.config['BLENDER_ID_LOGIN_CLIENT_SECRET'],
        user_id=None,
        url=None,
        _default_scopes='email',
        _redirect_uris=app.config['BLENDER_ID_LOGIN_CLIENT_REDIRECT_URIS'],
    )
    print('Adding new client to database')
    db.session.add(test_client)
    db.session.commit()

manager.run()
