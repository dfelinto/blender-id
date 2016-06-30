from datetime import datetime
from datetime import timedelta

from flask import jsonify
from flask import render_template
from flask import request
from flask import Blueprint

from flask.ext.security import current_user
from flask.ext.security import login_required
from flask_security.utils import verify_password

from application import app
from application import oauth
from application import db

from application.modules.oauth.model import Client
from application.modules.oauth.model import Grant
from application.modules.oauth.model import Token
from application.modules.users.model import User

oauth_api = Blueprint('oauth_api', __name__)


@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    expire_tokens()

    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    expire_tokens()

    # decide the expires time
    expires_secs = app.config['OAUTH2_PROVIDER_TOKEN_EXPIRES_IN']
    expires = datetime.now() + timedelta(seconds=expires_secs)

    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=current_user,
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    expire_tokens()

    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


def expire_tokens():
    """Deletes all expired authentication and grant tokens.

    Always call this before querying auth tokens or grants.
    """

    now = datetime.now()
    Token.query.filter(Token.expires <= now).delete()
    Grant.query.filter(Grant.expires <= now).delete()
    db.session.commit()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    expire_tokens()

    expires_in = token.pop('expires_in')
    expires = datetime.now() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok


@oauth.usergetter
def get_user(email, password, *args, **kwargs):
    user = User.query.filter_by(email=email).first()
    if verify_password(password, user.password):
        return user
    return None


@app.route('/oauth/authorize', methods=['GET', 'POST'])
@login_required
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.query.filter_by(client_id=client_id).first()
        # Check if a token already exists for a user. If so, skip authorization
        # screen.
        if Token.query.filter_by(client_id=client_id, user_id=current_user.id).first():
            return True
        kwargs['client'] = client
        kwargs['user'] = current_user
        kwargs['gravatar'] = current_user.gravatar(120, False)
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@app.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token():
    return None


@app.route('/oauth/revoke', methods=['POST'])
@login_required
@oauth.revoke_handler
def revoke_token(): pass


def split_name(full_name):
    # Backwards compatibility for full_name last_name
    if not full_name:
        return u'', u''

    name_split = full_name.split(u' ')
    half = len(name_split) // 2

    return (u' '.join(name_split[:half]),
            u' '.join(name_split[half:]))


@oauth_api.route('/user')
@oauth.require_oauth()
def user():
    self_user = request.oauth.user
    public_roles = {
        'bfct_trainer': False,
        'network_member': False}
    for role in public_roles:
        public_roles[role] = self_user.has_role(role)

    first_name, last_name = split_name(self_user.full_name)

    return jsonify(
        id=self_user.id,
        full_name=self_user.full_name,
        first_name=first_name,
        last_name=last_name,
        email=self_user.email,
        roles=public_roles)


@oauth_api.route('/me')
@oauth.require_oauth()
def me():
    return user()


@oauth_api.route('/address')
@oauth.require_oauth()
def address():
    user = request.oauth.user
    if user.address:
        address = user.address[0]
        return jsonify(
            address_type=address.address_type,
            first_name=address.first_name,
            last_name=address.last_name,
            street_address=address.street_address,
            extended_address=address.extended_address,
            locality=address.locality,
            region=address.region,
            postal_code=address.postal_code,
            country_code_alpha2=address.country_code_alpha2)
    else:
        return None


@app.route(oauth.error_uri)
def oauth_error():
    """Generic OAuth error handler."""
    return render_template('oauth_errors.html')
