from application import app
from application import db

from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import flash

from flask.ext.security import login_required
from flask.ext.security import url_for_security
from flask.ext.security.core import current_user

from application.modules.users.forms import ProfileForm
from application.modules.users.forms import AddressForm
from application.modules.users.model import Address

# Views
@app.route('/')
def homepage():
    if current_user.is_authenticated():
        return render_template('index.html', title='home')
    else:
        return redirect(url_for('about'))

@app.route('/about')
def about():
    return render_template('about.html', title='about')


@app.route('/settings/', methods=['POST', 'GET'])
@app.route('/settings/profile', methods=['POST', 'GET'])
@login_required
def profile():
    # Load the current data in the form
    cloud_communications = None;
    show_avatar = None;
    form = ProfileForm(
        blender_id=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        cloud_communications=cloud_communications,
        show_avatar=show_avatar)

    # Run if form is being submitted
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        #current_user.set_setting('cloud_communications',form.cloud_communications.data)
        #current_user.set_setting('show_avatar',form.show_avatar.data)
        db.session.commit()
        return redirect(url_for('homepage'))

    # Display form on GET request
    return render_template('settings/profile.html', 
        user=current_user, 
        form=form,
        gravatar_url=current_user.gravatar(120, False),
        title='profile')


@app.route('/settings/address', methods=['POST', 'GET'])
@login_required
def address():
    address = Address.query.filter_by(user_id=current_user.id).first()
    if address:
        form = AddressForm(
            first_name=address.first_name,
            last_name=address.last_name,
            street_address= address.street_address,
            extended_address=address.extended_address,
            locality=address.locality,
            region=address.region,
            postal_code=address.postal_code,
            country_code_alpha2=address.country_code_alpha2
            )
    else:
        form = AddressForm()

    if form.validate_on_submit():
        if address:
            address.first_name = form.first_name.data
            address.last_name = form.last_name.data
            address.street_address = form.last_name.data
            address.extended_address = form.extended_address.data
            address.locality = form.locality.data
            address.region = form.region.data
            address.postal_code = form.postal_code.data
            address.country_code_alpha2 = form.country_code_alpha2.data
            flash('Address updated!')
        else:
            address = Address(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                street_address=form.last_name.data,
                extended_address=form.extended_address.data,
                locality=form.locality.data,
                region=form.region.data,
                postal_code=form.postal_code.data,
                country_code_alpha2=form.country_code_alpha2.data)
            db.session.add(address)
            flash('Address added!')

        db.session.commit()
        return redirect(url_for('address'))

    # Display form on GET request
    return render_template('settings/address.html', 
        form=form,
        title='address')





