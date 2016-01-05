import uuid
from flask import jsonify
from flask import request
from flask_security.utils import verify_password

from application import app
from application import db

from application.modules.users.model import UsersRestTokens
from application.modules.users.model import user_datastore


@app.route('/u/identify', methods=['POST'])
def verify_identity():
    """Entry point that generates an authentication token, given exsiting
    and valid username and password. The token can be used as alternative
    authentication system for REST based services (e.g. Attract).
    """

    username = request.form['username']
    password = request.form['password']
    hostname = request.form['hostname']

    if hostname.endswith('.local'):
        hostname = hostname[:-6]

    user = user_datastore.get_user(username)
    if not user:
        return jsonify(status='fail', data=dict(
            username='User does not exist'))
    if not verify_password(password, user.password):
        # TODO Throttle authentication attempts (limit to 3 or 5)
        # We need to address the following cases:
        # - the user already has a token-hostname pair
        # - the user never autheticated before (where do we store such info?)
        return jsonify(status='fail', data=dict(password='Wrong password'))

    # Check if token already exists for that user and hostname
    user_rest_token = UsersRestTokens.query\
        .filter_by(user_id=user.id, hostname=hostname)\
        .first()

    if not user_rest_token:
        # Make new REST Token
        user_rest_token = UsersRestTokens(
            user_id=user.id,
            token=uuid.uuid1().hex,
            hostname=hostname)
        db.session.add(user_rest_token)
        db.session.commit()

    return jsonify(
        status='success',
        data=dict(
            user_id=user_rest_token.user_id,
            token=user_rest_token.token))


@app.route('/u/validate_token', methods=['POST'])
def validate_token():
    """Validate and existing authentication token. This is usually called by
    a third party (e.g. Attract) every few requests to confirm the identity
    of a user.
    """
    token = request.form['token']
    error = False

    try:
        token_info = UsersRestTokens.query.filter_by(token=token).one()
    except:
        token_info = None
        error = True

    if token_info:
        user = user_datastore.get_user(token_info.user_id)
        if user:
            user_info = {
                'email': user.email,
                'id': user.id
            }

    if not error and user:
        return jsonify(
            status='success',
            data=dict(
                user=user_info))
    else:
        response = jsonify(
            status='fail',
            data=dict(token='Token is invalid'))
        response.status_code = 403
        return response

