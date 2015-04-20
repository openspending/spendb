import urllib
import json

from spendb.core import db, data_manager
from spendb.model import Dataset, Run
from spendb.etl import tasks

from spendb.tests.base import DatabaseTestCase
from spendb.tests.helpers import csvimport_fixture_file
from spendb.tests.helpers import csvimport_fixture_path


def import_fixture(name):
    model_fp = csvimport_fixture_file(name, 'model.json')
    mapping_fp = csvimport_fixture_file(name, 'mapping.json')
    model = json.load(model_fp)
    if mapping_fp:
        model['mapping'] = json.load(mapping_fp)
    dataset = Dataset(model)
    db.session.add(dataset)
    data_path = csvimport_fixture_path(name, 'data.csv')
    db.session.commit()
    return dataset, data_path


class TestImportFixtures(DatabaseTestCase):

    def setUp(self):
        super(TestImportFixtures, self).setUp()
        data_manager._index = None
        self.s3_mock.start()

    def tearDown(self):
        super(TestImportFixtures, self).tearDown()
        self.s3_mock.stop()

    def count_lines_in_stream(self, f):
        from StringIO import StringIO
        return len(list(StringIO(f.read())))

    def _test_import(self, name, lines=None):
        dataset, url = import_fixture(name)
        data = urllib.urlopen(url)
        if lines is None:
            lines = self.count_lines_in_stream(data) - 1  # -1 for header row

        source = tasks.extract_url(dataset, url)
        tasks.transform_source(dataset, source.name)
        tasks.load(dataset, source_name=source.name)

        for run in db.session.query(Run).all():
            assert run.status == Run.STATUS_COMPLETE, run

        # check correct number of entries
        dataset = db.session.query(Dataset).first()
        entries = list(dataset.fact_table.entries())
        assert len(entries) == lines, len(entries)

    def test_imports_mexico(self):
        self._test_import('mexico')

    def test_imports_lbhf(self):
        self._test_import('lbhf')

    def test_imports_sample(self):
        self._test_import('sample')

    def test_imports_uganda(self):
        self._test_import('uganda')

    def test_imports_quoting(self):
        self._test_import('quoting', lines=5)

    def test_missing_url(self):
        dataset, url = import_fixture('file:///dev/null')
        source = tasks.extract_url(dataset, url)
        assert source is None, source

        for run in db.session.query(Run).all():
            assert run.status == Run.STATUS_FAILED, run

