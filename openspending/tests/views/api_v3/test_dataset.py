from flask import url_for

from openspending.core import db
from openspending.tests.base import ControllerTestCase
from openspending.tests.helpers import load_fixture


class TestSearchApiController(ControllerTestCase):

    def setUp(self):
        super(TestSearchApiController, self).setUp()
        self.cra = load_fixture('cra')

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

    def test_view_private_dataset(self):
        self.cra.private = True
        db.session.commit()
        url = url_for('datasets_api3.view', name=self.cra.name)
        res = self.client.get(url)
        assert '403' in res.status, res.status
