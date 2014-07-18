from application import app

from flask import render_template, redirect, url_for, request
from flask.ext.security import login_required
from flask.ext.security.core import current_user

from flask_wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import DataRequired

# Views
@app.route('/')
@login_required
def homepage():
    return render_template('index.html', title='home')

@app.route('/about')
def about():
    return render_template('about.html', title='about')


class ProfileForm(Form):
    blender_id = TextField('Blender-ID')
    first_name = TextField('First Name', validators=[DataRequired()])
    last_name = TextField('Last Name', validators=[DataRequired()])
    cloud_communications = BooleanField('Cloud Communications')
    show_avatar = BooleanField('Show Avatar')


@app.route('/settings/', methods=['POST', 'GET'])
@app.route('/settings/profile', methods=['POST', 'GET'])
@login_required
def profile():
    # Load the current data in the form
    form = ProfileForm(
        blender_id=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        cloud_communications=current_user.get_setting('cloud_communications'),
        show_avatar=current_user.get_setting('show_avatar'))

    # Run if form is being submitted
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.set_setting('cloud_communications',form.cloud_communications.data)
        current_user.set_setting('show_avatar',form.show_avatar.data)
        db.session.commit()
        return redirect(url_for('profile'))

    # Display form on GET request
    return render_template('settings/profile.html', 
        user=current_user, 
        form=form,
        gravatar_url=current_user.gravatar(120, False),
        title='profile')
