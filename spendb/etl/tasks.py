import logging

from archivekit import Source

from spendb.core import db
from spendb.etl.job import job
from spendb.etl.extract import validate_table, load_table

log = logging.getLogger(__name__)


@job(operation='Import from file')
def extract_fileobj(job, dataset, fh, file_name=None, mime_type=None):
    """ Upload contents of an opened fh to the data repository. """
    meta = {'source_file': file_name}
    if mime_type is not None:
        meta['mime_type'] = mime_type
    source = job.package.ingest(fh, meta=meta, overwrite=False)
    source.save()
    job.set_source(source)
    return source


@job(operation='Import from URL')
def extract_url(job, dataset, url):
    """ Upload contents of a URL to the data repository. """
    source = job.package.ingest(url, overwrite=False)
    if source is None:
        return
    source.save()
    job.set_source(source)
    return source


@job(operation='Clean up source data')
def transform_source(job, dataset, source_name):
    """ Transform the contents of an uploaded source dataset to a
    well-understood file format. """
    source = Source(job.package, source_name)
    job.set_source(source)
    source = validate_table(source)
    if source.meta.get('num_failed') > 0:
        return job.failed()
    return source


@job(operation='Load to database')
def load(job, dataset, source_name):
    """ Load the table artifact for this dataset into the fact
    table. """
    source = Source(job.package, source_name)
    job.set_source(source)
    dataset.data = {}
    dataset.fields = source.meta.get('fields', {})
    if not len(dataset.fields):
        raise ValueError('No columns recognized in source data.')

    db.session.commit()
    dataset.fact_table.drop()
    dataset.fact_table.create()
    dataset.fact_table.load_iter(load_table(source))
