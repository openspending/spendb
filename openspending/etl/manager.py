import logging

from boto.s3.connection import S3Connection, S3ResponseError
from boto.s3.connection import Location

log = logging.getLogger(__name__)


class DataManager(object):
    """ The data manager coordinates read and write access to the
    ETL data storage. """

    def __init__(self):
        self.bucket = None

    def init_app(self, app):
        self.bucket = self.get_bucket(app.config)

    def get_bucket(self, config):
        conn = S3Connection(config.get('AWS_KEY_ID'),
                            config.get('AWS_SECRET'))
        bucket_name = config.get('AWS_DATA_BUCKET', 'data.openspending.org')

        try:
            return conn.get_bucket(bucket_name)
        except S3ResponseError, se:
            if se.status == 404:
                return conn.create_bucket(bucket_name,
                                          location=Location.EU)
            else:
                log.exception(se)
