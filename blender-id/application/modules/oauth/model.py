import hashlib
import logging
import urllib

from application import app
from application import db

from flask.ext.security import (Security, 
    SQLAlchemyUserDatastore,
    UserMixin, 
    RoleMixin)
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)


class Client(db.Model):
    # human readable name
    name = db.Column(db.String(125))
    description = db.Column(db.String(400))
    picture = db.Column(db.String(125))

    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), nullable=False)

    user_id = db.Column(db.ForeignKey('user.id'))
    user = db.relationship('User')

    url = db.Column(db.String(256))

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    def __repr__(self):
        return 'Client(client_id=%s)' % self.client_id


class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'),
        nullable=False,
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)
    host_label = db.Column(db.String(255))

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


def create_oauth_client(client_config):
    """Creates an OAuth client in the database."""

    # Make sure the client only exists once
    client = Client.query.filter_by(client_id=client_config['id']).first()
    if client is not None:
        log.info('Removing pre-existing client %r from database', client_config['name'])
        db.session.delete(client)
    test_client = Client(
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
    log.info('Adding new client %r to database', client_config['name'])
    db.session.add(test_client)


def create_oauth_clients():
    """Creates the default OAuth clients from config.py.

     Default clients that already exist in the database will be removed and re-added.
     """

    for client_config in app.config['DEFAULT_CLIENTS']:
        create_oauth_client(client_config)
