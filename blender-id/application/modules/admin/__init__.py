from flask import render_template
from flask import redirect
from flask import url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin
from flask.ext import login
from flask.ext.admin import Admin
from flask.ext.admin import expose
from flask.ext.admin import form
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.base import BaseView
from flask.ext.admin.model.template import macro
from flask.ext.security import current_user
from flask.ext.security.utils import login_user

from werkzeug import secure_filename
from jinja2 import Markup
from wtforms import fields
from wtforms import validators
from wtforms import widgets
from wtforms.fields import SelectField
from wtforms.fields import TextField
import os, hashlib, time
import os.path as op

from application import app
from application import db
from application import thumb
from application.modules.users.model import user_datastore
from application.modules.users.model import User

def _list_items(view, context, model, name):
    """Utilities to upload and present images
    """
    if not model.name:
        return ''
    return Markup(
        '<div class="select2-container-multi">'
            '<ul class="select2-choices" style="border:0;cursor:default;background:none;">%s</ul></div>' % (
                ''.join( ['<li class="select2-search-choice" style="padding:3px 5px;">'
                            '<div>'+item.name+'</div></li>' for item in getattr(model,name)] )))


def _list_thumbnail(view, context, model, name):
    if not getattr(model,name):  #model.name only does not work because name is a string
        return ''
    return Markup('<img src="%s">' % url_for('static', 
        filename=thumb.thumbnail(getattr(model,name), '50x50', crop='fit')))

# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), '../../static/files',)
try:
    os.mkdir(file_path)
except OSError:
    pass


def prefix_name(obj, file_data):
    # Collect name and extension
    parts = op.splitext(file_data.filename)
    # Get current time (for unique hash)
    timestamp = str(round(time.time()))
    # Has filename only (not extension)
    file_name = secure_filename(timestamp + '%s' % parts[0])
    # Put them together
    full_name = hashlib.md5(file_name).hexdigest() + parts[1]
    return full_name


def image_upload_field(label):
    return form.ImageUploadField(label,
                    base_path=file_path,
                    thumbnail_size=(100, 100, True),
                    namegen=prefix_name,
                    endpoint='filemanager.static')



# Create customized views with access restriction
class CustomModelView(ModelView):
    def is_accessible(self):
        return login.current_user.has_role('admin')

class CustomBaseView(BaseView):
    def is_accessible(self):
        return login.current_user.has_role('admin')


class UserOperationsView(CustomBaseView):
    @expose('/')
    def index(self):
        return redirect(url_for('homepage'))
    @expose('/login/<int:user_id>/')
    def login(self, user_id):
        user = user_datastore.get_user(user_id)
        login_user(user)
        return redirect(url_for('homepage'))


class UserView(CustomModelView):
    column_list = ('email', 'active', 'first_name', 'last_name', 'user_operations')
    column_filters = ('id', 'email', 'active', 'first_name', 'last_name')
    column_formatters = dict(user_operations=macro('user_operations'))

    form_columns = ('email', 'first_name', 'last_name', 'active', 'roles')
    #column_formatters = dict(actions=lambda v, c, m, p: '<strong>asd</strong>')

    # form_rules = [
    #     # Header and four fields. Email field will go above phone field.
    #     rules.FieldSet(('first_name', 'last_name', 'email', 'roles'), 'Personal'),
    #     # Separate header and few fields
    #     rules.Macro('user_rule_macros.detail_tabs_head'),
    #     rules.Macro('user_rule_macros.billing', test=''),
    #     rules.Container('user_rule_macros.subscription', rules.Field('cloud_subscription')),
    #     rules.Container('user_rule_macros.address', rules.Field('address')),
    #     rules.Macro('user_rule_macros.detail_tabs_tail'),      
    # ]

    list_template = 'admin/user/list.html'


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if login.current_user.has_role('admin'):
            return self.render('admin/homepage.html')
            return super(MyAdminIndexView, self).index()
        else:
            return redirect(url_for('homepage'))

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('homepage'))


# Create admin backend
backend = admin.Admin(
    app, 
    'Blender ID', 
    index_view=MyAdminIndexView(), 
    base_template='admin/layout_admin.html'
)

backend.add_view(UserView(User, db.session, name='Users', url='users', endpoint='users'))
backend.add_view(UserOperationsView(name='User Operations', endpoint='user-operations', url='user-operations'))
