from flask import url_for

from spendb.core import db
from spendb.model import Dataset
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import load_fixture, make_account
from spendb.tests.helpers import data_fixture


class TestRunApiController(ControllerTestCase):

    def setUp(self):
        super(TestRunApiController, self).setUp()
        self.cra = load_fixture('cra')
        self.user = make_account('test')
        self.auth_qs = {'api_key': self.user.api_key}
        self.cra.managers.append(self.user)
        db.session.commit()
        url = url_for('sources_api.upload', dataset=self.cra.name)
        fh = data_fixture('cra')
        self.source = self.client.post(url, data={
            'file': (fh, 'cra.csv')
        }, query_string=self.auth_qs).json

    def test_runs_index(self):
        url = url_for('runs_api.index', dataset=self.cra.name)
        res = self.client.get(url)
        assert res.json['total'] == 1, res.json
        frst = res.json['results'][0]
        assert frst['status'] == 'complete', frst
        assert 'messages' not in frst, frst

    def test_runs_index_filter(self):
        url = url_for('runs_api.index', dataset=self.cra.name, source='foo')
        res = self.client.get(url)
        assert res.json['total'] == 0, res.json

    def test_runs_view(self):
        url = url_for('runs_api.view', dataset=self.cra.name, id=1)
        res = self.client.get(url)
        assert res.json['status'] == 'complete', res.json
        assert len(res.json['messages']), res.json
