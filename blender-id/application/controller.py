from application import app
from application import db

from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import flash
from flask import jsonify

from flask_security import login_required
from flask_security.core import current_user

from application.modules.users.forms import ProfileForm
from application.modules.users.forms import AddressForm
from application.modules.users.model import Address
from application.modules.oauth.model import Client

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
    form = ProfileForm(
        blender_id=current_user.email,
        full_name=current_user.full_name)

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
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
        if request.method == 'POST':
            form = AddressForm(request.form, address)
        else:
            form = AddressForm(
                first_name=address.first_name,
                last_name=address.last_name,
                street_address= address.street_address,
                extended_address=address.extended_address,
                locality=address.locality,
                region=address.region,
                postal_code=address.postal_code,
                )
            form.country_code_alpha2.data = address.country_code_alpha2
    else:
        form = AddressForm()

    if form.validate_on_submit():
        if address:
            address.first_name = form.first_name.data
            address.last_name = form.last_name.data
            address.street_address = form.street_address.data
            address.extended_address = form.extended_address.data
            address.locality = form.locality.data
            address.region = form.region.data
            address.postal_code = form.postal_code.data
            address.country_code_alpha2 = form.country_code_alpha2.data
            flash('Address updated!')
        else:
            address = Address(
                user_id=current_user.id,
                address_type='billing',
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                street_address=form.street_address.data,
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


@app.route('/settings/developer')
@login_required
def developer_index():
    """Basic entry point to view OAuth clients created by a developer.
    """
    user_clients = Client.query.filter_by(user_id=current_user.id).all()
    clients = []
    for c in user_clients:
        client = {
            'name': c.name,
            'client_id': c.client_id,
            'client_secret': c.client_secret,
            'redirect_uris': c._redirect_uris,
            'default_scopes': c._default_scopes,
            'url': c.url
        }
        clients.append(client)
    return jsonify(clients=clients)
