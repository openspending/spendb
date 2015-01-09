
from sqlalchemy import Integer, UnicodeText, Float, Unicode
from nose.tools import assert_raises

from openspending.tests.helpers import model_fixture, load_dataset
from openspending.tests.base import DatabaseTestCase

from openspending.core import data_manager


class TestDataManager(DatabaseTestCase):

    def setUp(self):
        super(TestDataManager, self).setUp()
        
    def test_manager(self):
        assert data_manager.bucket is not None, data_manager.bucket
        assert False, dir(data_manager.bucket)
