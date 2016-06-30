from flask_wtf import Form
from flask_security.forms import RegisterForm
from flask_security.forms import ConfirmRegisterForm
from flask_security.forms import Required
from wtforms import StringField
from wtforms import SelectField
from wtforms import BooleanField

from wtforms.validators import DataRequired
import pycountry


class ProfileForm(Form):
    blender_id = StringField('Blender-ID')
    full_name = StringField('Full Name', validators=[DataRequired()])


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(country.alpha2, country.name) for country in pycountry.countries]


class AddressForm(Form):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    street_address = StringField('Street Address', validators=[DataRequired()])
    extended_address = StringField('Extended Street Address')
    locality = StringField('City', validators=[DataRequired()])
    region = StringField('Region/State', validators=[DataRequired()])
    postal_code = StringField('ZIP Code', validators=[DataRequired()])
    country_code_alpha2 = CountrySelectField('Country', validators=[DataRequired()])


class ExtendedRegisterForm(RegisterForm, ConfirmRegisterForm):
    full_name = StringField('Full Name', [Required()])
