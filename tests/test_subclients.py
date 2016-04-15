# -*- encoding: utf-8 -*-

import datetime
import json
import logging

from common_test_class import AbstractBlenderIdTest

log = logging.getLogger(__name__)


class SubclientsTest(AbstractBlenderIdTest):
    def setUp(self):
        super(SubclientsTest, self).setUp()
        self.oauth_client_id = self.app.config['BLENDER_ID_ADDON_CLIENT_ID']

    def _create_test_user(self):
        user = self.create_user(email='test@example.com', password='password123',
                                first_name=u'ဦး',  # 'uncle' in Burmese
                                last_name=u'သီဟ',  # 'lion' in Burmese
                                )
        self.db.session.commit()  # We need to commit to get the user ID.

        token = self.create_token(user.id, self.oauth_client_id, 60)
        self.db.session.commit()

        return user.id, token.access_token

    def _create_scst(self, auth_token, subclient_id):
        rv = self.client.post('/subclients/create_token',
                              data={'subclient_id': subclient_id,
                                    'host_label': 'unittest'},
                              headers={'Authorization': 'Bearer %s' % auth_token})
        self.assertEqual(rv.status_code, 201)  # Should be 201 Created

        scst = json.loads(rv.data)
        return scst

    def _revoke_scst(self, auth_token, subclient_id, user_id, scst, client_id=None):
        rv = self.client.post('/subclients/revoke_token',
                              data={'client_id': client_id or self.oauth_client_id,
                                    'subclient_id': subclient_id,
                                    'user_id': user_id,
                                    'token': scst},
                              headers={'Authorization': 'Bearer %s' % auth_token})
        self.assertEqual(rv.status_code, 200)  # Should be 200 OK, even when token not found.
        return rv

    def test_create_token(self):
        subclient_id = 'CREATE-TOKEN-UNITTEST'

        # Test wrong HTTP method.
        rv = self.client.get('/subclients/create_token', data={'subclient_id': subclient_id})
        self.assertEqual(rv.status_code, 405)  # Should be Method Not Allowed.

        # Test unauthenticated call.
        rv = self.client.post('/subclients/create_token', data={'subclient_id': subclient_id})
        self.assertEqual(rv.status_code, 401)  # Should be 401 Unauthenticated.

        # Create user + OAuth token to enable authenticated calls.
        _, token = self._create_test_user()

        # Test authenticated call.
        scst = self._create_scst(token, subclient_id)

        self.assertEqual('success', scst['status'])
        self.assertTrue(scst['data']['token'])

        expires = datetime.datetime.strptime(scst['data']['expires'], '%a, %d %b %Y %H:%M:%S GMT')
        self.assertLess(datetime.datetime.now(), expires)

    def test_validate_token(self):
        subclient_id = 'VALIDATE-TOKEN-UNITTEST'

        # Test wrong HTTP method.
        rv = self.client.get('/u/validate_token',
                             data={'subclient_id': subclient_id,
                                   'user_id': 1234,
                                   'token': 'je moeder'})
        self.assertEqual(rv.status_code, 405)  # Should be 405 Method Not Allowed

        # Test nonexistant token.
        rv = self.client.post('/u/validate_token',
                              data={'subclient_id': subclient_id,
                                    'user_id': 1234,
                                    'token': 'je moeder'})
        self.assertEqual(rv.status_code, 403)  # Should be 403 Forbidden

        # Create a subclient-specific token to test with.
        user_id, token = self._create_test_user()
        scst = self._create_scst(token, subclient_id)

        # Test correct token
        rv = self.client.post('/u/validate_token',
                              data={'subclient_id': subclient_id,
                                    'user_id': user_id,
                                    'token': scst['data']['token']})
        self.assertEqual(rv.status_code, 200)  # Should be 200 OK

        # Test content
        resp = json.loads(rv.data)
        self.assertEqual(user_id, resp['user']['id'])
        self.assertEqual(u'test@example.com', resp['user']['email'])
        self.assertEqual(u'ဦး သီဟ', resp['user']['full_name'])

        expires = datetime.datetime.strptime(resp['token_expires'], '%a, %d %b %Y %H:%M:%S GMT')
        self.assertLess(datetime.datetime.now(), expires)

        # Test token without user id, should work too.
        rv = self.client.post('/u/validate_token',
                              data={'subclient_id': subclient_id,
                                    'user_id': '',
                                    'token': scst['data']['token']})
        self.assertEqual(rv.status_code, 200)  # Should be 200 OK

        # Test content
        resp = json.loads(rv.data)
        self.assertEqual(user_id, resp['user']['id'])
        self.assertEqual(u'test@example.com', resp['user']['email'])
        self.assertEqual(u'ဦး သီဟ', resp['user']['full_name'])

        expires = datetime.datetime.strptime(resp['token_expires'], '%a, %d %b %Y %H:%M:%S GMT')
        self.assertLess(datetime.datetime.now(), expires)

    def test_revoke_token(self):
        subclient_id = 'TEST-REVOKE-TOKEN'

        # Test wrong HTTP method.
        rv = self.client.get('/subclients/revoke_token',
                             data={'subclient_id': subclient_id,
                                   'user_id': 1234,
                                   'token': 'je moeder'})
        self.assertEqual(rv.status_code, 405)  # Should be 405 Method Not Allowed

        user_id, token = self._create_test_user()

        # Revoke nonexistant token.
        self._revoke_scst(token, subclient_id, 1234, 'je moeder')

        # Create a subclient-specific token to test with.
        scst = self._create_scst(token, subclient_id)

        def assert_access(expect_status):
            access_req = self.client.post('/u/validate_token',
                                          data={'subclient_id': subclient_id,
                                                'user_id': user_id,
                                                'token': scst['data']['token']})
            self.assertEqual(expect_status, access_req.status_code)

        # Nothing revoked, so we should have access.
        assert_access(200)

        # Revoke token for other client, shouldn't have any effect.
        self._revoke_scst(token, subclient_id, user_id, scst['data']['token'],
                          client_id='op je hoofd')
        assert_access(200)

        # Revoke token, should revoke access.
        self._revoke_scst(token, subclient_id, user_id, scst['data']['token'])
        assert_access(403)

    # FIXME: Uncomment when token expiry is reinstated.
    # def test_token_expiry(self):
    #     from application.modules.oauth import model as oauth_model
    #
    #     user_id, token = self._create_test_user()
    #
    #     minute = datetime.timedelta(minutes=1)
    #
    #     # Directly create some SCSTs.
    #     with self.app.test_request_context():
    #         token1 = oauth_model.Token(
    #             access_token='EXPIRED-OLD',
    #             client_id=self.oauth_client_id,
    #             user_id=user_id,
    #             subclient='unittest1',
    #             expires=datetime.datetime.utcnow() - 2 * minute,
    #             host_label='unittest',
    #         )
    #         self.db.session.add(token1)
    #
    #         token2 = oauth_model.Token(
    #             access_token='EXPIRED',
    #             client_id=self.oauth_client_id,
    #             user_id=user_id,
    #             subclient='unittest1',
    #             expires=datetime.datetime.utcnow() - minute,
    #             host_label='unittest',
    #         )
    #         self.db.session.add(token2)
    #
    #         token3 = oauth_model.Token(
    #             access_token='GOOD',
    #             client_id=self.oauth_client_id,
    #             user_id=user_id,
    #             subclient='unittest1',
    #             expires=datetime.datetime.utcnow() + minute,
    #             host_label='unittest',
    #         )
    #         self.db.session.add(token3)
    #         self.db.session.commit()
    #
    #         # All three subclient tokens + the main token should be in the database.
    #         all = oauth_model.Token.query.all()
    #         self.assertEqual(4, len(all), 'Database should contain 4 tokens, not %i' % len(all))
    #
    #         # Remove expired tokens and do a re-count.
    #         oauth_model.Token.expire_tokens()
    #         all = oauth_model.Token.query.all()
    #         self.assertEqual(2, len(all), 'Database should contain 2 tokens, not %i' % len(all))
    #
    #         subtoken = oauth_model.Token.query.filter_by(subclient='unittest1').one()
    #         self.assertEqual('GOOD', subtoken.access_token)
