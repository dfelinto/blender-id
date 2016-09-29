import datetime
import os
import hashlib
import time
import os.path
import logging

from flask import redirect
from flask import url_for
import flask

import flask_admin
import flask_admin.form
import flask_admin.base
import flask_admin.contrib.sqla
import flask_admin.model.template

import flask_login
import flask_security.utils
import flask_security.recoverable

import wtforms

from werkzeug.utils import secure_filename
from jinja2 import Markup

from application import app
from application import db
from application import thumb
from application.modules.users.model import user_datastore
from application.modules.users.model import User

log = logging.getLogger(__name__)


def _list_items(view, context, model, name):
    """Utilities to upload and present images
    """
    if not model.name:
        return ''
    return Markup(
        '<div class="select2-container-multi">'
        '<ul class="select2-choices" style="border:0;cursor:default;background:none;">%s</ul></div>' % (
            ''.join(['<li class="select2-search-choice" style="padding:3px 5px;">'
                     '<div>' + item.name + '</div></li>' for item in getattr(model, name)])))


def _list_thumbnail(view, context, model, name):
    if not getattr(model, name):  # model.name only does not work because name is a string
        return ''
    return Markup('<img src="%s">' % url_for('static',
                                             filename=thumb.thumbnail(getattr(model, name), '50x50',
                                                                      crop='fit')))


# Create directory for file fields to use
file_path = os.path.join(os.path.dirname(__file__), '../../static/files', )
try:
    os.mkdir(file_path)
except OSError:
    pass


def prefix_name(obj, file_data):
    # Collect name and extension
    parts = os.path.splitext(file_data.filename)
    # Get current time (for unique hash)
    timestamp = str(round(time.time()))
    # Has filename only (not extension)
    file_name = secure_filename(timestamp + '%s' % parts[0])
    # Put them together
    full_name = hashlib.md5(file_name).hexdigest() + parts[1]
    return full_name


def image_upload_field(label):
    return flask_admin.form.ImageUploadField(
        label,
        base_path=file_path,
        thumbnail_size=(100, 100, True),
        namegen=prefix_name,
        endpoint='filemanager.static')


# Create customized views with access restriction
class CustomModelView(flask_admin.contrib.sqla.ModelView):
    def is_accessible(self):
        return flask_login.current_user.has_role('admin')


class CustomBaseView(flask_admin.base.BaseView):
    def is_accessible(self):
        return flask_login.current_user.has_role('admin')


class UserOperationsView(CustomBaseView):
    @flask_admin.expose('/')
    def index(self):
        return redirect(url_for('homepage'))

    @flask_admin.expose('/login/<int:user_id>/')
    def login(self, user_id):
        user = user_datastore.get_user(user_id)
        flask_security.utils.login_user(user)
        return redirect(url_for('homepage'))


class UserView(CustomModelView):
    can_delete = False
    column_list = ('email', 'active', 'full_name', 'user_operations')
    column_filters = ('id', 'email', 'active', 'full_name')
    column_formatters = dict(user_operations=flask_admin.model.template.macro('user_operations'))
    form_columns = ('email', 'full_name', 'roles', 'initial_password')
    list_template = 'admin/user/list.html'

    form_extra_fields = {
        'initial_password': wtforms.PasswordField('Initial Password')
    }

    def on_model_change(self, form, user_model, is_created):
        if not is_created:
            return

        # Users created by an admin don't need email verification
        user_model.confirmed_at = datetime.datetime.now()
        user_model.active = True

        # Automatically send password-recover email, but only if the initial password was empty.
        send_reset_mail = False
        if not user_model.initial_password:
            user_model.initial_password = u'you really have to reset this password'
            send_reset_mail = True

        user_model.password = flask_security.utils.encrypt_password(user_model.initial_password)
        del user_model.initial_password

        if send_reset_mail:
            try:
                flask_security.recoverable.send_reset_password_instructions(user_model)
                flask.flash('Password reset email sent to %s' % user_model.email)
            except Exception as ex:
                log.exception('Error sending password-recover mail to %s', user_model.email)
                flask.flash(
                    'Unable to send password reset email to %s: %s' % (user_model.email, ex),
                    category='warning')
        else:
            flask.flash('DID NOT SEND Password reset email to %s, '
                        'you gave an initial password so send it yourself.' % user_model.email,
                        category='info')


# Create customized index view class that handles login & registration
class MyAdminIndexView(flask_admin.AdminIndexView):
    @flask_admin.expose('/')
    def index(self):
        if flask_login.current_user.has_role('admin'):
            return self.render(
                'admin/homepage.html')
        else:
            return redirect(url_for('homepage'))

    @flask_admin.expose('/logout/')
    def logout_view(self):
        flask_login.logout_user()
        return redirect(url_for('homepage'))


# Create admin backend
backend = flask_admin.Admin(
    app,
    'Blender ID',
    index_view=MyAdminIndexView(),
    base_template='admin/layout_admin.html'
)

backend.add_view(UserView(User, db.session, name='Users', url='users', endpoint='users'))
backend.add_view(
    UserOperationsView(name='User Operations', endpoint='user-operations', url='user-operations'))
