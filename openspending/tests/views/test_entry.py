from flask import url_for

from openspending.model.dataset import Dataset
from openspending.tests.base import ControllerTestCase
from openspending.tests.helpers import load_fixture


class TestRestController(ControllerTestCase):

    def setUp(self):
        super(TestRestController, self).setUp()
        load_fixture('cra')
        self.cra = Dataset.by_name('cra')

    def test_entry(self):
        q = self.cra.fact_table.mapping.columns['from.name'] == 'Dept047'
        example = list(self.cra.fact_table.entries(q, limit=1)).pop()

        response = self.client.get(url_for('entry.view',
                                    dataset=self.cra.name,
                                    format='json',
                                    id=str(example['id'])))

        assert '"id":' in response.data, response.data
        assert '"cofog1":' in response.data, response.data
        assert '"from":' in response.data, response.data
        assert '"Dept047"' in response.data, response.data


class TestEntryController(ControllerTestCase):

    def setUp(self):
        super(TestEntryController, self).setUp()
        load_fixture('cra')
        self.cra = Dataset.by_name('cra')

    def test_view(self):
        t = list(self.cra.fact_table.entries(limit=1)).pop()
        response = self.client.get(url_for('entry.view', dataset='cra',
                                           id=t['id']))
        assert 'cra' in response.data
