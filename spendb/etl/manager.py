import logging

from archivekit import open_collection

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
        if not self.configured:
            return
        if self._coll is None:
            env = self.app.config
            args = {
                'aws_key_id': env.get('AWS_KEY_ID'),
                'aws_secret': env.get('AWS_SECRET'),
                'bucket_name': env.get('AWS_DATA_BUCKET')
            }
            self._coll = open_collection('datasets', 's3', **args)
        return self._coll
