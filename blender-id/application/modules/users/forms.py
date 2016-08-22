from flask_wtf import Form
from flask_security.forms import RegisterForm
from flask_security.forms import ConfirmRegisterForm
from flask_security.forms import Required
from flask_security.forms import LoginForm
from wtforms import StringField
from wtforms import SelectField

from wtforms.validators import DataRequired
import pycountry


class ProfileForm(Form):
    blender_id = StringField('Blender-ID')
    full_name = StringField('Full Name', validators=[DataRequired()])


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [
            (country.alpha2, country.name) for country in pycountry.countries]


class AddressForm(Form):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    street_address = StringField('Street Address', validators=[DataRequired()])
    extended_address = StringField('Extended Street Address')
    locality = StringField('City', validators=[DataRequired()])
    region = StringField('Region/State', validators=[DataRequired()])
    postal_code = StringField('ZIP Code', validators=[DataRequired()])
    country_code_alpha2 = CountrySelectField('Country',
                                             validators=[DataRequired()])


class ExtendedRegisterForm(RegisterForm, ConfirmRegisterForm):
    full_name = StringField('Full Name', [Required()])


class NicerLoginForm(LoginForm):
    def __init__(self):
        super(NicerLoginForm, self).__init__()
        self.requires_confirmation = False

    def validate(self):
        valid = super(NicerLoginForm, self).validate()
        if valid:
            # Here we know that the user doesn't require confirmation.
            return True

        if not self.email.data.strip():
            # Unable to find user without email address.
            return False

        from flask_security.forms import _datastore
        from flask_security.confirmable import requires_confirmation

        user = _datastore.get_user(self.email.data)

        # Only show the 'Resend confirmation mail' button when the user
        # has actually authenticated properly.
        if user and not self.password.errors and requires_confirmation(user):
            self.requires_confirmation = True

        return False
