import json
from flask import url_for

from spendb.core import db
from spendb.tests.helpers import csvimport_fixture_path
from spendb.tests.base import ControllerTestCase
from spendb.tests.helpers import load_fixture, make_account


class TestSlicerApiController(ControllerTestCase):

    def setUp(self):
        super(TestSlicerApiController, self).setUp()
        self.cra = load_fixture('cra')
        self.user = make_account('test')
        self.auth_qs = {'api_key': self.user.api_key}
        self.cra.managers.append(self.user)
        self.cra_url = csvimport_fixture_path('../data', 'cra.csv')
        db.session.commit()

    def test_show_index(self):
        url = url_for('slicer.show_index')
        res = self.client.get(url)
        assert 'Cubes OLAP server' in res.data, res.data

    def test_list_cubes(self):
        url = url_for('slicer.list_cubes')
        res = self.client.get(url)
        assert len(res.json) == 1, res.json
        assert res.json[0]['name'] == 'cra', res.json

    def test_cube_model(self):
        url = url_for('slicer.cube_model', cube_name=self.cra.name)
        res = self.client.get(url)
        assert 'Country Regional Analysis' in res.json['description'], res.json
        assert len(res.json['dimensions']) == 12, len(res.json['dimensions'])
