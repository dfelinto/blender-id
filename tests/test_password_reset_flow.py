# -*- encoding: utf-8 -*-

from __future__ import absolute_import

import datetime
import json
import logging

import flask
import flask_security
import flask_security.recoverable

import mock

from common_test_class import AbstractBlenderIdTest

log = logging.getLogger(__name__)


class ManualUserCreationTest(AbstractBlenderIdTest):
    def setUp(self):
        AbstractBlenderIdTest.setUp(self)
        self.oauth_client_id = self.app.config['BLENDER_ID_ADDON_CLIENT_ID']
        self.admin_user_id = self._create_admin_user()
        self.user_role = self._create_role('cloud_demo')

    @mock.patch('flask_security.recoverable.send_mail')
    def test_manual_user_creation__no_password(self, mock_send_mail):
        self._create_user_through_admin(u'')
        mock_send_mail.assert_called_once()

        created_user = self._find_user(u'user@example.com')

        # Reset the password.
        with self.app.test_request_context():
            token = flask_security.recoverable.generate_reset_password_token(created_user)
            reset_link = flask_security.url_for_security('reset_password', token=token)

        resp = self.client.post(reset_link, data={
            'password': u'haha nieuw password ImKUjg8Vk3KEXuiLoRPC2L3KFcn3ydLA',
            'password_confirm': u'haha nieuw password ImKUjg8Vk3KEXuiLoRPC2L3KFcn3ydLA',
        })
        self.assertEqual(200, resp.status_code)

        # Check logging in with the new password.
        self._assert_can_log_in_via_form(u'user@example.com',
                                         u'haha nieuw password ImKUjg8Vk3KEXuiLoRPC2L3KFcn3ydLA')

    @mock.patch('flask_security.recoverable.send_mail')
    def test_manual_user_creation(self, mock_send_mail):
        self._create_user_through_admin(u'hae1chohteuKee0eepahJai1hochigoh')

        # Mail should not be sent due to an initial password being passed.
        mock_send_mail.assert_not_called()
        self._assert_can_log_in_via_form(u'user@example.com', u'hae1chohteuKee0eepahJai1hochigoh')

    def _assert_can_log_in_via_form(self, email, cleartext_password):
        with self.app.test_request_context():
            url = flask_security.url_for_security('login')

        resp = self.client.post(url, data={
            'email': email,
            'password': cleartext_password,
        })
        self.assertEqual(200, resp.status_code)

    def _create_user_through_admin(self, initial_password):
        with self.app.test_request_context():
            url = flask.url_for('users.create_view')

        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                sess['user_id'] = self.admin_user_id

            resp = c.post(url,
                          data={
                              'email': u'user@example.com',
                              'initial_password': initial_password,
                              'full_name': u'Mrs. Example',
                              'roles': self.user_role.id,
                          })
        self.assertEqual(302, resp.status_code)

    def _list_routes(self):
        from pprint import pprint
        from flask import url_for

        def has_no_empty_params(rule):
            defaults = rule.defaults if rule.defaults is not None else ()
            arguments = rule.arguments if rule.arguments is not None else ()
            return len(defaults) >= len(arguments)

        links = []
        with self.app.test_request_context():
            for rule in self.app.url_map.iter_rules():
                # Filter out rules we can't navigate to in a browser
                # and rules that require parameters
                if "GET" in rule.methods and has_no_empty_params(rule):
                    url = url_for(rule.endpoint, **(rule.defaults or {}))
                    links.append((url, rule.endpoint))

        links.sort(key=lambda t: len(t[0]) + 100 * ('/api/' in t[0]))

        pprint(links)

    def _create_test_user(self):
        user = self.create_user(email='test@example.com', password='password123',
                                full_name=u'ဦး သီဟ',  # 'uncle lion' in Burmese
                                )
        self.db.session.commit()  # We need to commit to get the user ID.
        return user

    def _create_role(self, name):
        import application.modules.users
        role = application.modules.users.user_datastore.find_or_create_role(name)
        self.db.session.commit()
        self.db.session.flush()
        self.assertTrue(role.id > 0)  # required to fetch the user ID.
        return role

    def _create_admin_user(self):
        import application.modules.users

        role = self._create_role('admin')

        admin_user = self._create_test_user()
        application.modules.users.user_datastore.add_role_to_user(admin_user, role)
        self.db.session.commit()
        self.db.session.flush()
        self.assertTrue(admin_user.id > 0)  # required to fetch the user ID.
        return admin_user.id

    def _find_user(self, email):
        import application.modules.users
        return application.modules.users.user_datastore.find_user(email=email)
