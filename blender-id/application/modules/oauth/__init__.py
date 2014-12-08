from datetime import datetime
from datetime import timedelta

from flask import redirect
from flask import jsonify
from flask import render_template
from flask import request
from flask import session
from flask import Blueprint

from flask.ext.security import current_user
from flask.ext.security import login_required
from werkzeug.security import gen_salt

from application import app
from application import oauth
from application import db

from application.modules.oauth.model import Client
from application.modules.oauth.model import Grant
from application.modules.oauth.model import Token
#from application.modules.users.model import user_datastore

oauth_api = Blueprint('oauth_api', __name__)

# @app.route('/client')
# def client():
#     if not current_user.is_authenticated():
#         return redirect('/')
#     item = Client(
#         client_id=gen_salt(40),
#         client_secret=gen_salt(50),
#         _redirect_uris=' '.join([
#             'http://localhost:8000/authorized',
#             'http://127.0.0.1:8000/authorized',
#             'http://127.0.1:8000/authorized',
#             'http://127.1:8000/authorized',
#             ]),
#         _default_scopes='email',
#         user_id=current_user.id,
#     )
#     db.session.add(item)
#     db.session.commit()
#     return jsonify(
#         client_id=item.client_id,
#         client_secret=item.client_secret,
#     )


@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.now() + timedelta(seconds=100)
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
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.query.filter_by(
        client_id=request.client.client_id,
        user_id=request.user.id
    )
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

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


@app.route('/oauth/token')
@oauth.token_handler
def access_token():
    return None


@app.route('/oauth/authorize', methods=['GET', 'POST'])
@login_required
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        kwargs['user'] = current_user
        kwargs['gravatar'] = current_user.gravatar(120, False)
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@app.route('/oauth/revoke', methods=['POST'])
@login_required
@oauth.revoke_handler
def revoke_token(): pass


@oauth_api.route('/user')
@oauth.require_oauth()
def user():
    user = request.oauth.user
    public_roles = {
        'bfct_trainer':False,
        'network_freelance':False,
        'network_academic':False,
        'network_corporate':False}
    for role in public_roles:
        public_roles[role] = user.has_role(role)

    return jsonify(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        roles=public_roles)


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
