from application import app, db
from application.model import user_datastore, User

from flask import render_template, redirect, url_for
from flask.ext import admin, login
from flask.ext.admin import Admin, expose, form
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.base import BaseView
from flask.ext.admin.model.template import macro

from flask.ext.security.utils import login_user

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
