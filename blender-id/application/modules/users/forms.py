from flask_wtf import Form
from flask_security.forms import RegisterForm
from flask_security.forms import Required
from wtforms import StringField
from wtforms import SelectField
from wtforms import BooleanField

from wtforms.validators import DataRequired

from application.modules.countries.model import Country


class ProfileForm(Form):
    blender_id = StringField('Blender-ID')
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    cloud_communications = BooleanField('Cloud Communications')
    show_avatar = BooleanField('Show Avatar')


class AddressForm(Form):
    countries = [(country.code, country.name) for country in Country.query.all()]

    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    street_address = StringField('Street Address', validators=[DataRequired()])
    extended_address = StringField('Extended Street Address')
    locality = StringField('City', validators=[DataRequired()])
    region = StringField('Region/State', validators=[DataRequired()])
    postal_code = StringField('ZIP Code', validators=[DataRequired()])
    country_code_alpha2 = SelectField('Country', choices=countries, validators=[DataRequired()])


class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name', [Required()])
    last_name = StringField('Last Name', [Required()])
