import logging

from loadkit import extract, transform, logfile
from loadkit import Source, Artifact

from openspending.core import data_manager, db
from openspending.model.denorm_fact_table import FactTable

log = logging.getLogger(__name__)

ARTIFACT_NAME = 'table.json'
MODULES = ['openspending', 'messytables']


def capture_logs(package, run):
    pass


def extract_fileobj(dataset, fh, file_name=None):
    """ Upload contents of an opened fh to the data repository. """
    package = data_manager.package(dataset.name)
    handler = logfile.capture(package, 'test', MODULES)
    try:
        source = extract.from_fileobj(package, fh, source_name=file_name)
        return source
    except Exception, e:
        log.exception(e)
    finally:
        handler.archive()
    

def extract_url(dataset, url):
    """ Upload contents of a URL to the data repository. """
    package = data_manager.package(dataset.name)
    handler = logfile.capture(package, 'test', MODULES)
    try:
        source = extract.from_url(package, url)
        return source
    except Exception, e:
        log.exception(e)
    finally:
        handler.archive()
    

def transform_source(dataset, source_name):
    """ Transform the contents of an uploaded source dataset to a
    well-understood file format. """
    package = data_manager.package(dataset.name)
    handler = logfile.capture(package, 'test', MODULES)
    try:
        source = Source(package, source_name)
        artifact = transform.to_table(source, ARTIFACT_NAME)

        # TODO: log when there was no data.
        return artifact
    except Exception, e:
        log.exception(e)
    finally:
        handler.archive()


def load(dataset):
    """ Load the table artifact for this dataset into the fact
    table. """
    package = data_manager.package(dataset.name)
    handler = logfile.capture(package, 'test', MODULES)
    try:
        dataset.fields = package.manifest.get('fields', {})
        if not len(dataset.fields):
            log.error('No columns recognized in source data.')
            return

        db.session.commit()

        artifact = Artifact(package, ARTIFACT_NAME)
        fact_table = FactTable(dataset)
        fact_table.create()
        fact_table.load_iter(artifact.records())
        
        # TODO: log when there was no data.
        return fact_table
    except Exception, e:
        log.exception(e)
    finally:
        handler.archive()
