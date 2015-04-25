import tempfile

from archivekit import open_collection
from flask.ext.testing import TestCase as FlaskTestCase

from spendb.core import create_web_app, data_manager
from spendb.tests.helpers import clean_db, init_db


class TestCase(FlaskTestCase):

    def create_app(self):
        app = create_web_app(**{
            'DEBUG': True,
            'TESTING': True,
            'SITE_TITLE': 'SpenDB',
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'CELERY_ALWAYS_EAGER': True
        })
        data_manager._coll = open_collection('test', 'file',
                                             path=tempfile.mkdtemp())
        return app

    def setUp(self):
        init_db(self.app)

    def tearDown(self):
        clean_db(self.app)


class DatabaseTestCase(TestCase):
    pass


class ControllerTestCase(DatabaseTestCase):
    pass
