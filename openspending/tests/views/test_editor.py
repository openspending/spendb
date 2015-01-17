import json

from flask import url_for

from openspending.tests.base import ControllerTestCase
from openspending.tests.helpers import make_account, load_fixture
from openspending.model.dataset import Dataset

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

    def test_dimensions_update_invalid_json(self):
        response = self.client.post(url_for('editor.dimensions_update', dataset='cra'),
                                    data={'mapping': 'banana'},
                                    query_string={'api_key': self.user.api_key})
        assert '400' in response.status, response.status

    def test_dimensions_update_valid_json(self):
        response = self.client.post(url_for('editor.dimensions_update', dataset='cra'),
                                    data={'mapping': """{
                                                          "amount": {
                                                            "column": "IMPORTE PEF",
                                                            "datatype": "float",
                                                            "default_value": "",
                                                            "description": null,
                                                            "label": "Amount",
                                                            "type": "measure"
                                                          },
                                                          "theid": {
                                                            "attributes": {
                                                              "label": {
                                                                "column": "FF",
                                                                "datatype": "string",
                                                                "default_value": ""
                                                              },
                                                              "name": {
                                                                "column": "id",
                                                                "datatype": "id",
                                                                "default_value": ""
                                                              }
                                                            },
                                                            "description": null,
                                                            "key": true,
                                                            "label": "Theid",
                                                            "type": "compound"
                                                          },
                                                          "time": {
                                                            "column": "DATE",
                                                            "datatype": "date",
                                                            "default_value": "",
                                                            "description": null,
                                                            "format": null,
                                                            "label": "Time",
                                                            "type": "date"
                                                          }
                                                        }"""},
                                    query_string={'api_key': self.user.api_key})
        assert '200' in response.status, response.status

    def test_views_edit_mask(self):
        response = self.client.get(url_for('editor.views_edit', dataset='cra'),
                                   query_string={'api_key': self.user.api_key})
        assert '"default"' in response.data
        assert 'Update' in response.data

    def test_views_update(self):
        cra = Dataset.by_name('cra')
        views = cra.data['views']
        views[0]['label'] = 'Banana'
        response = self.client.post(url_for('editor.views_update', dataset='cra'),
                                    data={'views': json.dumps(views)},
                                    query_string={'api_key': self.user.api_key})
        assert '200' in response.status, response.status
        cra = Dataset.by_name('cra')
        assert 'Banana' in repr(cra.data['views'])

    def test_views_update_invalid_json(self):
        response = self.client.post(url_for('editor.views_update', dataset='cra'),
                                    data={'views': 'banana'},
                                    query_string={'api_key': self.user.api_key})
        assert '400' in response.status, response.status

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
