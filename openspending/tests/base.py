import tempfile

from moto import mock_s3
from flask.ext.testing import TestCase as FlaskTestCase

from openspending.core import create_web_app
from openspending.tests.helpers import clean_db, init_db


class TestCase(FlaskTestCase):

    def create_app(self):
        self.s3_mock = mock_s3()
        
        self.s3_mock.start()
        app = create_web_app(**{
            'DEBUG': True,
            'TESTING': True,
            # if this ever exists, something went horribly wrong:
            'AWS_DATA_BUCKET': 'unittest.openspending.org',
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'CELERY_ALWAYS_EAGER': True,
            'UPLOADS_DEFAULT_DEST': tempfile.mkdtemp()
        })
        self.s3_mock.stop()
        return app

    def setUp(self):
        init_db(self.app)

    def tearDown(self):
        clean_db(self.app)


class DatabaseTestCase(TestCase):
    pass


class ControllerTestCase(DatabaseTestCase):
    pass
