from spendb.tests.base import DatabaseTestCase

from spendb.core import data_manager


class TestDataManager(DatabaseTestCase):

    def setUp(self):
        data_manager._index = None
        super(TestDataManager, self).setUp()

    def tearDown(self):
        super(TestDataManager, self).tearDown()

    def test_manager(self):
        assert data_manager.collection is not None, data_manager.collection
        package = data_manager.package('cra')
        assert package.id == 'cra', package
