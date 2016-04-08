"""Subclient support.

This allows an application (the client, such as Blender) to authenticate
against different applications (the subclients, such as Pillar) without
passing the user's actual authentication token to the subclient.

Users can request a SubClient-Specific Token (SCST), which can later be
verified by the subclient.

Subclients are identified by their unique subclient ID, which must be known
to both the client and the subclient.
"""

import logging
import datetime

from flask import request, Blueprint, jsonify, json
import oauthlib.common

from application import oauth, db, app
from . import model

subclients = Blueprint('subclients', __name__)
log = logging.getLogger(__name__)


@subclients.route('/create_token', methods=['POST'])
@oauth.require_oauth()
def create_token():
    """Creates a subclient-specific token.

    Must be an authenticated call.
    """

    subclient_id = request.form['subclient_id']
    host_label = request.form.get('host_label')

    log.info('Creating subclient token for user %r, client %r, subclient %r',
             request.oauth.user, request.oauth.client, subclient_id)

    if not subclient_id:
        log.warning('validate_token(): empty subclient ID given.')
        return jsonify({'status': 'fail',
                        'message': 'Subclient ID is invalid.'}), 400

    expires = datetime.datetime.utcnow() + datetime.timedelta(
        **app.config['SUBCLIENT_SPECIFIC_TOKEN_EXPIRY'])

    scst = model.SubclientToken(subclient_specific_token=oauthlib.common.generate_token(),
                                client=request.oauth.client,
                                subclient_id=subclient_id,
                                user=request.oauth.user,
                                expires=expires,
                                host_label=host_label)

    db.session.add(scst)
    db.session.commit()

    log.debug('Token created succesfully')

    return jsonify({
        'status': 'success',
        'data': {
            'scst': scst.subclient_specific_token,
            'expires': scst.expires,
        }
    }), 201


@subclients.route('/validate_token', methods=['POST'])
def validate_token():
    """Validates the given subclient-specific token.

    This is called by the subclient, to verify a user-supplied SCST.

    Returns further information about the user if the given token is valid.
    """

    client_id = request.form['client_id']
    subclient_id = request.form['subclient_id']
    user_id = int(request.form['user_id'])
    scst = request.form['scst']

    log.info('Validating subclient-specific token for client %s, subclient %s, user %s',
             client_id, subclient_id, user_id)

    model.SubclientToken.expire_tokens()
    token = model.SubclientToken.query.filter_by(client_id=client_id,
                                                 subclient_id=subclient_id,
                                                 user_id=user_id,
                                                 subclient_specific_token=scst).first()
    if token is None:
        log.debug('Token not found in database.')
        return jsonify({'status': 'fail'}), 404

    user = token.user
    full_name = u'%s %s' % (user.first_name, user.last_name)
    return jsonify({'status': 'success',
                    'user': {'email': user.email,
                             'full_name': full_name}}), 200


@subclients.route('/revoke_token', methods=['POST'])
@oauth.require_oauth()
def revoke_token():
    """Revokes a subclient-specific token."""

    client_id = request.form['client_id']
    subclient_id = request.form['subclient_id']
    user_id = int(request.form['user_id'])
    scst = request.form['scst']

    log.info('Revoking subclient-specific token for client %r, subclient %r, user %r',
             client_id, subclient_id, user_id)

    model.SubclientToken.query.filter_by(client_id=client_id,
                                         subclient_id=subclient_id,
                                         user_id=user_id,
                                         subclient_specific_token=scst).delete()
    db.session.commit()

    return jsonify({'status': 'success'}), 200
