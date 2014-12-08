from wtforms import SelectField

from application import app
from application import db

from application.modules.oauth.model import Client

from application.modules.admin import *
from application.modules.admin import _list_thumbnail


class ClientView(CustomModelView):
    column_searchable_list = ('name',)
    column_list = ('name', 'picture')
    column_formatters = { 'picture': _list_thumbnail }

    form_extra_fields = {
    'picture': image_upload_field('Logo'),
    }

    form_ajax_refs = {
        'user': {
            'fields': ('first_name', 'last_name', 'email'),
            'page_size': 10
        }
    }

# Add views
backend.add_view(ClientView(Client, db.session, name='OAuth Clients', url='oauth-clients'))
