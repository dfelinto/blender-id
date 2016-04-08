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
                                    'scst': scst},
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
        self.assertTrue(scst['data']['scst'])

        expires = datetime.datetime.strptime(scst['data']['expires'], '%a, %d %b %Y %H:%M:%S GMT')
        self.assertLess(datetime.datetime.now(), expires)

    def test_validate_token(self):
        subclient_id = 'VALIDATE-TOKEN-UNITTEST'

        # Test wrong HTTP method.
        rv = self.client.get('/subclients/validate_token',
                             data={'client_id': 'op je hoofd',
                                   'subclient_id': subclient_id,
                                   'user_id': 1234,
                                   'scst': 'je moeder'})
        self.assertEqual(rv.status_code, 405)  # Should be 405 Method Not Allowed

        # Test nonexistant token.
        rv = self.client.post('/subclients/validate_token',
                              data={'client_id': self.oauth_client_id,
                                    'subclient_id': subclient_id,
                                    'user_id': 1234,
                                    'scst': 'je moeder'})
        self.assertEqual(rv.status_code, 404)  # Should be 404 Not Found

        # Create a subclient-specific token to test with.
        user_id, token = self._create_test_user()
        scst = self._create_scst(token, subclient_id)

        # Test token for other client
        rv = self.client.post('/subclients/validate_token',
                              data={'client_id': 'op je hoofd',
                                    'subclient_id': subclient_id,
                                    'user_id': user_id,
                                    'scst': scst['data']['scst']})
        self.assertEqual(rv.status_code, 404)  # Should be 404 Not Found

        # Test token for correct client
        rv = self.client.post('/subclients/validate_token',
                              data={'client_id': self.oauth_client_id,
                                    'subclient_id': subclient_id,
                                    'user_id': user_id,
                                    'scst': scst['data']['scst']})
        self.assertEqual(rv.status_code, 200)  # Should be 200 OK

        # Test content
        resp = json.loads(rv.data)
        self.assertEqual(u'test@example.com', resp['user']['email'])
        self.assertEqual(u'ဦး သီဟ', resp['user']['full_name'])

    def test_revoke_token(self):
        subclient_id = 'TEST-REVOKE-TOKEN'

        # Test wrong HTTP method.
        rv = self.client.get('/subclients/revoke_token',
                             data={'client_id': 'op je hoofd',
                                   'subclient_id': subclient_id,
                                   'user_id': 1234,
                                   'scst': 'je moeder'})
        self.assertEqual(rv.status_code, 405)  # Should be 405 Method Not Allowed

        user_id, token = self._create_test_user()

        # Revoke nonexistant token.
        self._revoke_scst(token, subclient_id, 1234, 'je moeder')

        # Create a subclient-specific token to test with.
        scst = self._create_scst(token, subclient_id)

        def assert_access(expect_status):
            access_req = self.client.post('/subclients/validate_token',
                                          data={'client_id': self.oauth_client_id,
                                                'subclient_id': subclient_id,
                                                'user_id': user_id,
                                                'scst': scst['data']['scst']})
            self.assertEqual(expect_status, access_req.status_code)

        # Nothing revoked, so we should have access.
        assert_access(200)

        # Revoke token for other client, shouldn't have any effect.
        self._revoke_scst(token, subclient_id, user_id, scst['data']['scst'],
                          client_id='op je hoofd')
        assert_access(200)

        # Revoke token, should revoke access.
        self._revoke_scst(token, subclient_id, user_id, scst['data']['scst'])
        assert_access(404)

    def test_token_expiry(self):
        from application.modules.subclients import model

        user_id, token = self._create_test_user()

        minute = datetime.timedelta(minutes=1)

        # Directly create some SCSTs.
        with self.app.test_request_context():
            token1 = model.SubclientToken(
                subclient_specific_token='EXPIRED-OLD',
                client_id=self.oauth_client_id,
                user_id=user_id,
                subclient_id='unittest1',
                expires=datetime.datetime.utcnow() - 2 * minute,
                host_label='unittest',
            )
            self.db.session.add(token1)

            token2 = model.SubclientToken(
                subclient_specific_token='EXPIRED',
                client_id=self.oauth_client_id,
                user_id=user_id,
                subclient_id='unittest1',
                expires=datetime.datetime.utcnow() - minute,
                host_label='unittest',
            )
            self.db.session.add(token2)

            token3 = model.SubclientToken(
                subclient_specific_token='GOOD',
                client_id=self.oauth_client_id,
                user_id=user_id,
                subclient_id='unittest1',
                expires=datetime.datetime.utcnow() + minute,
                host_label='unittest',
            )
            self.db.session.add(token3)
            self.db.session.commit()

            # All three tokens should be in the database.
            all = model.SubclientToken.query.all()
            self.assertEqual(3, len(all), 'Database should contain 3 SCSTs, not %i' % len(all))

            # Remove expired tokens and do a re-count.
            model.SubclientToken.expire_tokens()
            all = model.SubclientToken.query.all()
            self.assertEqual(1, len(all), 'Database should contain 1 SCST, not %i' % len(all))

            self.assertEqual('GOOD', all[0].subclient_specific_token)
