from flask import url_for

from spendb.tests.base import ControllerTestCase


class TestMetaApiController(ControllerTestCase):

    def setUp(self):
        super(TestMetaApiController, self).setUp()
        
    def test_reference_data(self):
        url = url_for('meta_api.reference_data')
        res = self.client.get(url)
        assert 'territories' in res.json, res.json
        assert 'currencies' in res.json, res.json
        assert 'languages' in res.json, res.json
        
