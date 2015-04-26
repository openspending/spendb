import json
from flask import url_for

from spendb.core import db
from spendb.model import Dataset
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import load_fixture, make_account


class TestDatasetApiController(ControllerTestCase):

    def setUp(self):
        super(TestDatasetApiController, self).setUp()
        self.cra = load_fixture('cra')
        self.user = make_account('test')
        self.auth_qs = {'api_key': self.user.api_key}
        self.cra.managers.append(self.user)
        db.session.commit()

    def test_source_index(self):
        url = url_for('sources_api3.index')
        res = self.client.get(url)
        assert not res, res.json()
