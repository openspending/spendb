import logging

from loadkit import create

from boto.s3.connection import S3Connection, S3ResponseError
from boto.s3.connection import Location

log = logging.getLogger(__name__)


class DataManager(object):
    """ The data manager coordinates read and write access to the
    ETL data storage. """

    def __init__(self):
        self.app = None
        self._coll = None

    @property
    def configured(self):
        return self.app is not None

    def init_app(self, app):
        self.app = app

    def package(self, dataset):
        """ Get a package for a given dataset name. """
        assert self.configured, 'Data manager not configured!'
        return self.collection.get(dataset)

    @property
    def collection(self):
        if self.configured:
            if self._coll is None:
                env = self.app.config
                self._coll = create('s3', aws_key_id=env.get('AWS_KEY_ID'),
                                    aws_secret=env.get('AWS_SECRET'),
                                    bucket_name=env.get('AWS_DATA_BUCKET'))
            return self._coll
