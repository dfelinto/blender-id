import hashlib, urllib
from application import app
from application import db

from application.helpers import convert_to_type, convert_to_db_format

from flask.ext.security import (Security, 
    SQLAlchemyUserDatastore,
    UserMixin, 
    RoleMixin)
from sqlalchemy.orm.exc import NoResultFound

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
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
        except(NoResultFound): #no previous entry for this setting
            setting_value = UsersSettings(
                user_id=self.id,
                setting_id=setting.id,
                unconstrained_value=convert_to_db_format(value, setting.data_type))
        else: #previous entry exist, just updating the value
            setting_value.unconstrained_value=convert_to_db_format(value, setting.data_type)

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
        # In case the setting does not exist, we set it to the default and actually
        # make an entry in the database for it
        except(NoResultFound):
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

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


## --------- User Settings ---------

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
