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

    def test_list_datasets(self):
        url = url_for('datasets_api.index')
        res = self.client.get(url)
        assert res.json.get('total') == 1, res.json
        res0 = res.json.get('results')[0]
        assert res0.get('name') == self.cra.name, res0

    def test_list_private_datasets(self):
        self.cra.private = True
        db.session.commit()
        url = url_for('datasets_api.index')
        res = self.client.get(url)
        assert res.json.get('total') == 0, res.json
        assert len(res.json.get('results')) == 0, res.json

    def test_view_dataset(self):
        url = url_for('datasets_api.view', name=self.cra.name)
        res = self.client.get(url)
        assert res.json.get('name') == self.cra.name, res.json
        assert res.json.get('label') == self.cra.label, res.json

    def test_view_nonexisting_dataset(self):
        url = url_for('datasets_api.view', name='foo')
        res = self.client.get(url)
        assert '404' in res.status, res.status

    def test_view_private_dataset(self):
        self.cra.private = True
        db.session.commit()
        url = url_for('datasets_api.view', name=self.cra.name)
        res = self.client.get(url)
        assert '403' in res.status, res.status

    def test_view_model(self):
        url = url_for('datasets_api.model', name='cra')
        res = self.client.get(url)
        assert '200' in res.status, res.status
        assert 'cap_or_cur' in res.json['dimensions'], res.json
        assert 'cofog3' in res.json['dimensions'], res.json
        assert isinstance(res.json['dimensions']['cofog3'], dict), \
            res.json['dimensions']['cofog3']

    def test_view_fields(self):
        url = url_for('datasets_api.structure', name='cra')
        res = self.client.get(url)
        fields = res.json.get('fields')
        assert '200' in res.status, res.status
        assert 'cap_or_cur' in fields, res.json
        assert 'cofog1_name' in fields, res.json
        c1n = fields['cofog1_name']
        assert c1n['title'] == 'cofog1.name', c1n

    def test_view_fields_empty(self):
        cra = Dataset.by_name('cra')
        cra.fields = {}
        db.session.commit()
        url = url_for('datasets_api.structure', name='cra')
        res = self.client.get(url)
        fields = res.json.get('fields')
        assert 'cap_or_cur' not in fields, res.json

    def test_create_dataset(self):
        url = url_for('datasets_api.create')
        res = self.client.post(url, data=json.dumps({}),
                               query_string=self.auth_qs,
                               headers={'content-type': 'application/json'})
        assert '400' in res.status, res.status
        assert 'errors' in res.json, res.json

        params = {'name': 'testds', 'label': 'Test Dataset',
                  'category': 'budget', 'description': 'I\'m a banana!',
                  'currency': 'EUR'}
        data = json.dumps(params)
        res = self.client.post(url, data=data,
                               query_string=self.auth_qs,
                               headers={'content-type': 'application/json'})
        assert "200" in res.status, res.status
        assert res.json['name'] == 'testds', res.json

        ds = Dataset.by_name('testds')
        assert ds.label == params['label'], ds

    def test_update(self):
        data = {'name': 'cra', 'label': 'Common Rough Act',
                'description': 'I\'m a banana',
                'currency': 'EUR', 'languages': ['en'],
                'territories': ['gb'],
                'category': 'budget'}
        self.client.post(url_for('datasets_api.update', name='cra'),
                         data=json.dumps(data),
                         headers={'content-type': 'application/json'},
                         query_string={'api_key': self.user.api_key})
        cra = Dataset.by_name('cra')
        assert cra.label == 'Common Rough Act', cra.label
        assert cra.currency == 'EUR', cra.currency

    def test_update_invalid_category(self):
        data = {'name': 'cra',
                'label': 'Common Rough Act',
                'description': 'I\'m a banana',
                'currency': 'EUR', 'languages': ['en'],
                'territories': ['gb'], 'category': 'foo'}
        response = self.client.post(url_for('datasets_api.update', name='cra'),
                                    data=json.dumps(data),
                                    headers={'content-type': 'application/json'},
                                    query_string={'api_key': self.user.api_key})
        assert '400' in response.status, response.status
        assert 'valid category' in response.data
        cra = Dataset.by_name('cra')
        assert cra.label != 'Common Rough Act', cra.label

    def test_update_invalid_label(self):
        data = {'name': 'cra', 'label': '',
                'description': 'I\'m a banana',
                'currency': 'GBP'}
        response = self.client.post(url_for('datasets_api.update', name='cra'),
                                    data=json.dumps(data),
                                    headers={'content-type': 'application/json'},
                                    query_string={'api_key': self.user.api_key})
        assert '400' in response.status, response.status
        assert 'Required' in response.data
        cra = Dataset.by_name('cra')
        assert cra.label != '', cra.label

    def test_update_invalid_language(self):
        data = {'name': 'cra', 'label': 'CRA',
                'languages': ['esperanto'],
                'description': 'I\'m a banana',
                'currency': 'GBP'}
        response = self.client.post(url_for('datasets_api.update', name='cra'),
                                    data=json.dumps(data),
                                    headers={'content-type': 'application/json'},
                                    query_string={'api_key': self.user.api_key})
        assert '400' in response.status, response.status
        assert 'updated' not in response.data
        cra = Dataset.by_name('cra')
        assert 'esperanto' not in cra.languages

    def test_update_invalid_territory(self):
        data = {'name': 'cra', 'label': 'CRA',
                'territories': ['su'],
                'description': 'I\'m a banana',
                'currency': 'GBP'}
        response = self.client.post(url_for('datasets_api.update', name='cra'),
                                    data=json.dumps(data),
                                    headers={'content-type': 'application/json'},
                                    query_string={'api_key': self.user.api_key})
        assert '400' in response.status, response.status
        assert 'updated' not in response.data
        cra = Dataset.by_name('cra')
        assert 'su' not in cra.territories

    def test_update_invalid_currency(self):
        data = {'name': 'cra',
                'label': 'Common Rough Act',
                'description': 'I\'m a banana',
                'category': 'budget',
                'currency': 'glass pearls'}
        response = self.client.post(url_for('datasets_api.update', name='cra'),
                                    data=json.dumps(data),
                                    headers={'content-type': 'application/json'},
                                    query_string={'api_key': self.user.api_key})
        assert 'not a valid currency' in response.data
        cra = Dataset.by_name('cra')
        assert cra.currency == 'GBP', cra.label

    def test_update_model(self):
        url = url_for('datasets_api.update_model', name='cra')
        data = self.cra.model_data.copy()
        del data['dimensions']['cofog3']
        res = self.client.post(url, data=json.dumps(data),
                               headers={'content-type': 'application/json'},
                               query_string={'api_key': self.user.api_key})
        assert 'cofog3' not in res.json.get('dimensions', {}), res.json.keys()
        assert 'cofog1' in res.json.get('dimensions', {}), res.json.keys()

        res2 = self.client.get(url,
                               query_string={'api_key': self.user.api_key})
        assert res.json.keys() == res2.json.keys(), res2.json

    def test_update_model_invalid(self):
        url = url_for('datasets_api.update_model', name='cra')
        data = self.cra.model_data.copy()
        del data['dimensions']['cofog3']['label']
        res = self.client.post(url, data=json.dumps(data),
                               headers={'content-type': 'application/json'},
                               query_string={'api_key': self.user.api_key})
        assert '400' in res.status, res.status
        assert 'cofog3' in res.json.get('dimensions', {}), res.data

    def test_update_model_invalid_json(self):
        url = url_for('datasets_api.update_model', name='cra')
        data = 'huhu'
        res = self.client.post(url, data=json.dumps(data),
                               headers={'content-type': 'application/json'},
                               query_string={'api_key': self.user.api_key})
        assert '400' in res.status, res.status

    def test_publish(self):
        cra = Dataset.by_name('cra')
        cra.private = True
        db.session.commit()
        url = url_for('datasets_api.view', name='cra')
        res = self.client.get(url)
        assert '403' in res.status, res.status
        res = self.client.get(url, query_string={'api_key': self.user.api_key})
        assert '200' in res.status, res.status
        data = res.json.copy()
        data['category'] = 'budget'
        data['private'] = False
        response = self.client.post(url, data=json.dumps(data),
                                    headers={'content-type': 'application/json'},
                                    query_string={'api_key': self.user.api_key})
        assert '200' in response.status, response.json
        cra = Dataset.by_name('cra')
        assert cra.private is False, cra.private

    def test_delete_dataset(self):
        name = self.cra.name
        url = url_for('datasets_api.delete', name=name)
        res = self.client.delete(url, query_string=self.auth_qs)
        assert '410' in res.status, res.status
        ds = Dataset.by_name(name)
        assert ds is None, ds

    def test_delete_dataset_requires_auth(self):
        name = self.cra.name
        url = url_for('datasets_api.delete', name=name)
        res = self.client.delete(url, query_string={})
        assert '403' in res.status, res.status
        ds = Dataset.by_name(name)
        assert ds is not None, ds
