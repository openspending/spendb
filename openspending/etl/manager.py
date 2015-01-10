import logging

from loadkit import PackageIndex

from boto.s3.connection import S3Connection, S3ResponseError
from boto.s3.connection import Location

log = logging.getLogger(__name__)


class DataManager(object):
    """ The data manager coordinates read and write access to the
    ETL data storage. """

    def __init__(self):
        self.app = None
        self._index = None

    @property
    def configured(self):
        return self.app is not None

    def init_app(self, app):
        self.app = app

    def package(self, dataset):
        """ Get a package for a given dataset name. """
        assert self.configured, 'Data manager not configured!'
        return self.index.get(dataset)

    @property
    def index(self):
        if self.configured:
            if self._index is None:
                self._index = PackageIndex(self.get_bucket())
            return self._index

    def get_bucket(self):
        """ Connect to the S3 bucket. """
        conn = S3Connection(self.app.config.get('AWS_KEY_ID'),
                            self.app.config.get('AWS_SECRET'))
        bucket_name = self.app.config.get('AWS_DATA_BUCKET',
                                          'data.openspending.org')

        try:
            return conn.get_bucket(bucket_name)
        except S3ResponseError, se:
            if se.status == 404:
                return conn.create_bucket(bucket_name,
                                          location=Location.EU)
            else:
                log.exception(se)
