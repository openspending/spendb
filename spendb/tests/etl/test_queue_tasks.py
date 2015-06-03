from archivekit import Source

from spendb.core import db, data_manager
from spendb.model import Dataset
from spendb import tasks

from spendb.tests.helpers import meta_fixture
from spendb.tests.helpers import csvimport_fixture_path
from spendb.tests.base import DatabaseTestCase


class TestQueueTasks(DatabaseTestCase):

    def setUp(self):
        super(TestQueueTasks, self).setUp()
        data_manager._index = None
        self.dsn = 'cra'
        model = meta_fixture(self.dsn)
        self.ds = Dataset(model)
        db.session.add(self.ds)
        db.session.commit()
        self.cra_url = csvimport_fixture_path('../data', 'cra.csv')

    def tearDown(self):
        super(TestQueueTasks, self).tearDown()

    def test_load_from_url(self):
        tasks.load_from_url(self.dsn, self.cra_url)
        package = data_manager.package(self.dsn)
        sources = list(package.all(Source))
        assert len(sources) == 1, sources
        src0 = sources[0]
        assert src0.meta['name'] == 'cra.csv', src0.meta.items()

    def test_load_from_source(self):
        tasks.load_from_url(self.dsn, self.cra_url)
        package = data_manager.package(self.dsn)
        sources = list(package.all(Source))
        src0 = sources[0]
        tasks.load_from_source(self.dsn, src0.name)
