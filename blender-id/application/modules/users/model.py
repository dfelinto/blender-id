import hashlib
import urllib
import datetime
import uuid
from sqlalchemy.orm.exc import NoResultFound
from flask_security import SQLAlchemyUserDatastore
from flask_security import UserMixin
from flask_security import RoleMixin

from application import db
from application.helpers import convert_to_type
from application.helpers import convert_to_db_format

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return str(self.name)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    full_name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False, default='')
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)

    address = db.relationship('Address', backref='user')
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def set_setting(self, name, value):
        setting = Setting.query.\
            filter(Setting.name == name).\
            one()
        try:
            setting_value = UsersSettings.query.\
                filter_by(user_id=self.id, setting_id=setting.id).\
                one()
        except NoResultFound:
            # No previous entry for this setting
            setting_value = UsersSettings(
                user_id=self.id,
                setting_id=setting.id,
                unconstrained_value=convert_to_db_format(value, setting.data_type))
        else:
            # Previous entry exist, just updating the value
            setting_value.unconstrained_value = convert_to_db_format(value, setting.data_type)
        db.session.add(setting_value)
        db.session.commit()
        pass

    def get_setting(self, name):
        setting = Setting.query.\
            filter(Setting.name == name).\
            one()
        try:
            setting_value = UsersSettings.query.\
                filter_by(user_id=self.id, setting_id=setting.id).\
                one().unconstrained_value
        # In case the setting does not exist, we set it to the default and
        # actually make an entry for it
        except NoResultFound:
            self.set_setting(name, convert_to_type(setting.default, setting.data_type))
            setting_value = setting.default

        return convert_to_type(setting_value, setting.data_type)

    def gravatar(self, size=120, consider_settings=True):
        anonymous = False
        if consider_settings:
            anonymous = not (self.get_setting('show_avatar'))
        parameters = {'s':str(size), 'd':'mm'}
        if anonymous:
            parameters['f'] = 'y'

        return "https://www.gravatar.com/avatar/" + \
            hashlib.md5(self.email.lower()).hexdigest() + \
            "?" + urllib.urlencode(parameters)

    def __str__(self):
        return str(self.email)

    def __repr__(self):
        return 'User(id=%i, email=%r)' % (self.id, self.email)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class UsersRestTokens(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    hostname = db.Column(db.String(128))

    @property
    def creation_date(self):
        u = uuid.UUID(self.token)
        return datetime.datetime.fromtimestamp(
            (u.time - 0x01b21dd213814000L)*100/1e9)

    def __str__(self):
        return str(self.token)


class Address(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address_type = db.Column(db.String(128))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    street_address = db.Column(db.String(255))
    extended_address = db.Column(db.String(255))
    locality = db.Column(db.String(128))
    region = db.Column(db.String(255))
    postal_code = db.Column(db.String(24))
    country_code_alpha2 = db.Column(db.String(2))

    def __str__(self):
        return str(self.id)


class Setting(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128))
    data_type = db.Column(db.String(128), nullable=False)
    default = db.Column(db.String(128), nullable=False)

    def __str__(self):
        return self.name


class UsersSettings(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User, backref='users_settings')
    setting_id = db.Column(db.Integer, db.ForeignKey('setting.id'))
    setting = db.relationship(Setting, backref='users_settings')
    unconstrained_value = db.Column(db.String(128))

    def __str__(self):
        return self.user_id
