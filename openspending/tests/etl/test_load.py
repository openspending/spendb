from StringIO import StringIO

from openspending.core import db, data_manager
from openspending.model import Dataset
from openspending.etl import tasks

from openspending.tests.helpers import model_fixture
from openspending.tests.helpers import csvimport_fixture_path
from openspending.tests.helpers import csvimport_fixture_file
from openspending.tests.base import DatabaseTestCase


class TestLoad(DatabaseTestCase):

    def setUp(self):
        super(TestLoad, self).setUp()
        model = model_fixture('cra')
        self.ds = Dataset(model)
        db.session.add(self.ds)
        db.session.commit()
        self.cra_url = csvimport_fixture_path('../data', 'cra.csv')

    def test_extract_url(self):
        source = tasks.extract_url(self.ds, self.cra_url)
        assert 'cra.csv' == source.name, source.name
        
    #def test_extract_missing_url(self):
    #    url = csvimport_fixture_path('../data', 'xcra.csv')
    #    source = tasks.extract_url(self.ds.name, url)
    #    assert 'cra.csv' == source.name, source.name
    
    def test_extract_file(self):
        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        assert 'cra2.csv' == source.name, source.name

        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2 HUHU.csv')
        assert 'cra2-huhu.csv' == source.name, source.name
        
    def test_transform_source(self):
        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        art = tasks.transform_source(self.ds, source.name)
        assert art.name == tasks.ARTIFACT_NAME, art.name
        rows = list(art.records())
        assert len(rows) == 36, rows
        assert 'cofog1_label' in rows[1], rows[1]
        assert 'cofog1.label' not in rows[1], rows[1]

    def test_field_detection(self):
        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        tasks.transform_source(self.ds, source.name)
        package = data_manager.package(self.ds.name)
        fields = package.manifest.get('fields')
        assert len(fields) == 34, len(fields)
        assert 'amount' in fields, fields
        amt = fields.get('amount')
        assert amt['type'] == 'integer', amt

