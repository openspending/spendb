import json
from flask import url_for

from spendb.core import db
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import load_fixture, make_account


class TestSessionApiController(ControllerTestCase):

    def setUp(self):
        super(TestSessionApiController, self).setUp()
        self.cra = load_fixture('cra')
        self.user = make_account('test')
        self.auth_qs = {'api_key': self.user.api_key}
        self.cra.managers.append(self.user)
        db.session.commit()

    def test_not_logged_in(self):
        url = url_for('sessions_api.session')
        res = self.client.get(url)
        assert res.json.get('logged_in') is False, res.json
        assert res.json.get('user') is None, res.json

    def test_logged_in(self):
        url = url_for('sessions_api.session')
        res = self.client.get(url, query_string=self.auth_qs)
        assert res.json.get('logged_in') is True, res.json
        assert res.json.get('user') is not None, res.json

    def test_logout(self):
        url = url_for('sessions_api.logout')
        res = self.client.post(url, query_string=self.auth_qs)
        assert res.json.get('status') == 'ok', res.json

    def test_login_ok(self):
        url = url_for('sessions_api.login')
        cred = {'login': 'test', 'password': 'password'}
        res = self.client.post(url, data=json.dumps(cred),
                               headers={'content-type': 'application/json'})
        assert res.json.get('status') == 'ok', res.json
        assert res.status_code == 200, res.json

    def test_login_fail(self):
        url = url_for('sessions_api.login')
        cred = {'login': 'test', 'password': 'wrong'}
        res = self.client.post(url, data=json.dumps(cred),
                               headers={'content-type': 'application/json'})
        assert res.json.get('status') == 'error', res.json
        assert res.status_code == 400, res.json
