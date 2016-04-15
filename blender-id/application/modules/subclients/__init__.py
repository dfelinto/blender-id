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
from application.modules.oauth import model as oauth_model

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

    expires = datetime.datetime.now() + datetime.timedelta(
        **app.config['SUBCLIENT_SPECIFIC_TOKEN_EXPIRY'])

    scst = oauth_model.Token(access_token=oauthlib.common.generate_token(),
                             client=request.oauth.client,
                             subclient=subclient_id,
                             token_type='Bearer',
                             user=request.oauth.user,
                             expires=expires,
                             host_label=host_label)

    db.session.add(scst)
    db.session.commit()

    log.debug('Token created succesfully')

    return jsonify({
        'status': 'success',
        'data': {
            'token': scst.access_token,
            'expires': scst.expires,
        }
    }), 201


@subclients.route('/validate_token', methods=['POST'])
def validate_token():
    """Validates the given subclient-specific token.

    This is called by the subclient, to verify a user-supplied SCST.

    Returns further information about the user if the given token is valid.
    """

    subclient = request.form.get('subclient_id')
    user_id = request.form['user_id']
    access_token = request.form['token']

    log.info('Validating token for subclient %s, user "%s", token "%s"',
             subclient, user_id, access_token)

    filters = {'subclient': subclient,
               'access_token': access_token}
    if user_id:
        filters['user_id'] = int(user_id)

    # FIXME: properly delete expired tokens.
    token = oauth_model.Token.query.filter_by(**filters).first()

    if token is None:
        log.debug('Token not found in database.')
        return jsonify({'status': 'fail'}), 404

    user = token.user
    full_name = u'%s %s' % (user.first_name, user.last_name)
    return jsonify({'status': 'success',
                    'user': {'user_id': user.id,
                             'email': user.email,
                             'full_name': full_name},
                    'token_expires': token.expires,
                    }), 200


@subclients.route('/revoke_token', methods=['POST'])
@oauth.require_oauth()
def revoke_token():
    """Revokes a subclient-specific token."""

    client_id = request.form['client_id']
    subclient_id = request.form['subclient_id']
    user_id = int(request.form['user_id'])
    token = request.form['token']

    log.info('Revoking subclient-specific token for client %r, subclient %r, user %r',
             client_id, subclient_id, user_id)

    oauth_model.Token.query.filter_by(client_id=client_id,
                                      subclient=subclient_id,
                                      user_id=user_id,
                                      access_token=token).delete()
    db.session.commit()

    return jsonify({'status': 'success'}), 200
