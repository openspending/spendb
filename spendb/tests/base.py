import tempfile

from moto import mock_s3
from mock import patch
from archivekit import open_collection
from flask.ext.testing import TestCase as FlaskTestCase

from openspending.core import create_web_app, data_manager
from openspending.tests.helpers import clean_db, init_db, CPI


class TestCase(FlaskTestCase):

    def create_app(self):
        self.s3_mock = mock_s3()

        app = create_web_app(**{
            'DEBUG': True,
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'CELERY_ALWAYS_EAGER': True,
            'UPLOADS_DEFAULT_DEST': tempfile.mkdtemp()
        })
        data_manager._coll = open_collection('test', 'file',
                                             path=tempfile.mkdtemp())
        return app

    def setUp(self):
        init_db(self.app)
        patcher = patch('economics.data.get')
        mod = patcher.start()
        mod.return_value = CPI

    def tearDown(self):
        clean_db(self.app)


class DatabaseTestCase(TestCase):
    pass


class ControllerTestCase(DatabaseTestCase):
    pass
