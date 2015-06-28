from loadkit import logger

from spendb.core import db, data_manager
from spendb.model import Dataset, Run
from spendb.etl import tasks

from spendb.tests.helpers import meta_fixture
from spendb.tests.helpers import csvimport_fixture_path
from spendb.tests.helpers import csvimport_fixture_file
from spendb.tests.base import DatabaseTestCase


class TestLoad(DatabaseTestCase):

    def setUp(self):
        super(TestLoad, self).setUp()
        data_manager._index = None
        model = meta_fixture('cra')
        self.ds = Dataset(model)
        db.session.add(self.ds)
        db.session.commit()
        self.cra_url = csvimport_fixture_path('../data', 'cra.csv')

    def tearDown(self):
        super(TestLoad, self).tearDown()

    def test_extract_url(self):
        source = tasks.extract_url(self.ds, self.cra_url)
        assert 'cra.csv' == source.name, source.name

    def test_extract_missing_url(self):
        url = csvimport_fixture_path('../data', 'xcra.csv')
        source = tasks.extract_url(self.ds, url)
        assert source is None, source

        run = db.session.query(Run).first()
        package = data_manager.package(self.ds.name)
        messages = list(logger.load(package, run.id))
        assert len(messages) > 2, messages

    def test_extract_file(self):
        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        assert 'cra2.csv' == source.name, source.name

        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2 HUHU.csv')
        assert 'cra2-huhu.csv' == source.name, source.name

    def test_duplicate_file(self):
        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        assert 'cra2.csv' == source.name, source.name

        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        assert 'cra2-2.csv' == source.name, source.name

    def test_transform_source(self):
        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        src = tasks.transform_source(self.ds, source.name)
        assert src.name == source.name, src.name
        rows = list(tasks.load_table(src))
        assert len(rows) == 36, rows
        assert 'cofog1_label' in rows[1], rows[1]
        assert 'cofog1.label' not in rows[1], rows[1]

    def test_field_detection(self):
        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        source = tasks.transform_source(self.ds, source.name)
        fields = source.meta.get('fields')
        assert len(fields) == 34, len(fields)
        by_name = {f['name']: f for f in fields}
        assert 'amount' in by_name, fields
        amt = by_name.get('amount')
        assert amt['type'] == 'integer', amt

    def test_load_data(self):
        fp = csvimport_fixture_file('../data', 'cra.csv')
        source = tasks.extract_fileobj(self.ds, fp,
                                       file_name='cra2.csv')
        tasks.transform_source(self.ds, source.name)
        tasks.load(self.ds, source.name)
        assert self.ds.fact_table.num_entries() == 36, \
            self.ds.fact_table.num_entries()

        entries = list(self.ds.fact_table.entries())
        assert len(entries) == 36, entries
