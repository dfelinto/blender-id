import uuid
# import base64
from flask import jsonify
from flask import request

from flask_security.utils import verify_password
# from flask_security.utils import encrypt_password
# from flask_security.utils import get_hmac

from application import app
from application import db

from application.modules.users.model import UsersRestTokens
from application.modules.users.model import user_datastore


@app.route('/u/identify', methods=['POST'])
def verify_identity():
    username = request.form['username']
    password = request.form['password']
    hostname = request.form['hostname']

    if hostname.endswith('.local'):
        hostname = hostname[:-6]

    user = user_datastore.get_user(username)
    if not user:
        return jsonify(message='User does not exist')
    if not verify_password(password, user.password):
        return jsonify(message='Wrong password')

    # Make new REST Token
    user_rest_token = UsersRestTokens(
        user_id=user.id,
        token=uuid.uuid1().hex,
        hostname=hostname)
    db.session.add(user_rest_token)
    db.session.commit()

    return jsonify(
        token=user_rest_token.token,
        message='You are logged in')


@app.route('/u/validate_token', methods=['POST'])
def validate_token():
    token = request.form['token']
    count = UsersRestTokens.query.filter_by(token=token)
    if count>0:
        return jsonify(
            valid=True,
            message='Valid token')
    else:
        return jsonify(
            valid=False,
            message='Invalid token')
