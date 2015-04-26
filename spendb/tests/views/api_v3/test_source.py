import json
from flask import url_for

from spendb.core import db
from spendb.model import Dataset
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import load_fixture, make_account
from spendb.tests.helpers import data_fixture


class TestDatasetApiController(ControllerTestCase):

    def setUp(self):
        super(TestDatasetApiController, self).setUp()
        self.cra = load_fixture('cra')
        self.user = make_account('test')
        self.auth_qs = {'api_key': self.user.api_key}
        self.cra.managers.append(self.user)
        db.session.commit()

    def test_source_index(self):
        url = url_for('sources_api3.index', dataset=self.cra.name)
        res = self.client.get(url)
        assert res.json['total'] == 0, res.json

    def test_source_upload_anon(self):
        url = url_for('sources_api3.upload', dataset=self.cra.name)
        fh = data_fixture('cra')
        res = self.client.post(url, data={
            'file': (fh, 'cra.csv')
        })
        assert '403' in res.status, res.status

    def test_source_upload(self):
        url = url_for('sources_api3.upload', dataset=self.cra.name)
        fh = data_fixture('cra')
        res = self.client.post(url, data={
            'file': (fh, 'cra.csv')
        }, query_string=self.auth_qs)
        assert '403' not in res.status, res.status
