import json
from flask import url_for

from openspending.tests.base import ControllerTestCase


class TestHomeController(ControllerTestCase):

    def test_index(self):
        response = self.client.get(url_for('home.index'))
        assert 'OpenSpending' in response.data

    def test_locale(self):
        set_l = url_for('home.set_locale')
        data = json.dumps({'locale': 'en'})
        self.client.post(set_l, data=data,
                         headers={'Content-Type': 'application/json'})
