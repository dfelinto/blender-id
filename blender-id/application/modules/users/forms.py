from flask_wtf import Form
from wtforms import StringField
from wtforms import SelectField
from wtforms import TextField
from wtforms import BooleanField

from wtforms.validators import DataRequired

from application.modules.countries.model import Country


class ProfileForm(Form):
    blender_id = TextField('Blender-ID')
    first_name = TextField('First Name', validators=[DataRequired()])
    last_name = TextField('Last Name', validators=[DataRequired()])
    cloud_communications = BooleanField('Cloud Communications')
    show_avatar = BooleanField('Show Avatar')


class AddressForm(Form):
    countries = [(country.code, country.name) for country in Country.query.all()]

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    street_address = StringField('Street Address', validators=[DataRequired()])
    extended_address = StringField('Extended Street Address', validators=[DataRequired()])
    locality = StringField('City', validators=[DataRequired()])
    region = StringField('Region/Country', validators=[DataRequired()])
    postal_code = StringField('ZIP Code', validators=[DataRequired()])
    country_code_alpha2 = SelectField('Country', choices=countries, validators=[DataRequired()])
