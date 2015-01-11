from flask import url_for

from openspending.core import db
from openspending.model import Dataset
from openspending.tests.base import ControllerTestCase
from openspending.tests.helpers import load_fixture, make_account


class TestSearchApiController(ControllerTestCase):

    def setUp(self):
        super(TestSearchApiController, self).setUp()
        self.cra = load_fixture('cra')
        self.user = make_account('test')
        self.auth_qs = {'api_key': self.user.api_key}
        self.cra.managers.append(self.user)
        db.session.commit()

    def test_list_datasets(self):
        url = url_for('datasets_api3.index')
        res = self.client.get(url)
        assert res.json.get('total') == 1, res.json
        res0 = res.json.get('results')[0]
        assert res0.get('name') == self.cra.name, res0

    def test_list_private_datasets(self):
        self.cra.private = True
        db.session.commit()
        url = url_for('datasets_api3.index')
        res = self.client.get(url)
        assert res.json.get('total') == 0, res.json
        assert len(res.json.get('results')) == 0, res.json

    def test_view_dataset(self):
        url = url_for('datasets_api3.view', name=self.cra.name)
        res = self.client.get(url)
        assert res.json.get('name') == self.cra.name, res.json
        assert res.json.get('label') == self.cra.label, res.json

    def test_view_nonexisting_dataset(self):
        url = url_for('datasets_api3.view', name='foo')
        res = self.client.get(url)
        assert '404' in res.status, res.status

    def test_view_private_dataset(self):
        self.cra.private = True
        db.session.commit()
        url = url_for('datasets_api3.view', name=self.cra.name)
        res = self.client.get(url)
        assert '403' in res.status, res.status

    def test_delete_dataset(self):
        name = self.cra.name
        url = url_for('datasets_api3.delete', name=name)
        res = self.client.delete(url, query_string=self.auth_qs)
        assert '410' in res.status, res.status
        ds = Dataset.by_name(name)
        assert ds is None, ds
    
    def test_delete_dataset_requires_auth(self):
        name = self.cra.name
        url = url_for('datasets_api3.delete', name=name)
        res = self.client.delete(url, query_string={})
        assert '403' in res.status, res.status
        ds = Dataset.by_name(name)
        assert ds is not None, ds
