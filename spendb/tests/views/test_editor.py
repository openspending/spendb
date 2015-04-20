import json

from flask import url_for

from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import make_account, load_fixture
from spendb.model.dataset import Dataset

from unittest import skip


@skip('Need to re-do editor')
class TestEditorController(ControllerTestCase):

    def setUp(self):
        super(TestEditorController, self).setUp()
        self.user = make_account('test')
        load_fixture('cra', self.user)

    def test_overview(self):
        response = self.client.get(url_for('editor.index', dataset='cra'),
                                   query_string={'api_key': self.user.api_key})
        assert 'Manage the dataset' in response.data

    def test_team_edit_mask(self):
        response = self.client.get(url_for('editor.team_edit', dataset='cra'),
                                   query_string={'api_key': self.user.api_key})
        assert 'Add someone' in response.data
        assert 'Save' in response.data

    def test_team_update(self):
        response = self.client.post(url_for('editor.team_update', dataset='cra'),
                                    data={},
                                    query_string={'api_key': self.user.api_key})
        assert '200' in response.status, response.status
        cra = Dataset.by_name('cra')
        assert len(cra.managers.all()) == 1, cra.managers
