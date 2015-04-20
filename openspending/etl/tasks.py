import logging

from archivekit import Source
from loadkit.types.table import Table
from loadkit.operators.table import TableExtractOperator

from openspending.core import db
from openspending.etl.job import job

log = logging.getLogger(__name__)

ARTIFACT_NAME = 'table.json'


@job(operation='Load from file')
def extract_fileobj(job, dataset, fh, file_name=None):
    """ Upload contents of an opened fh to the data repository. """
    meta = {'source_file': file_name}
    source = job.package.ingest(fh, meta=meta, overwrite=False)
    source.save()
    job.set_source(source)
    return source


@job(operation='Load from URL')
def extract_url(job, dataset, url):
    """ Upload contents of a URL to the data repository. """
    source = job.package.ingest(url, overwrite=False)
    source.save()
    job.set_source(source)
    return source


@job(operation='Clean up source data')
def transform_source(job, dataset, source_name):
    """ Transform the contents of an uploaded source dataset to a
    well-understood file format. """
    source = Source(job.package, source_name)
    job.set_source(source)
    op = TableExtractOperator(None, None, {})
    table = Table(job.package, ARTIFACT_NAME)
    artifact = op.transform(source, table)

    # TODO: log when there was no data.
    return artifact


@job(operation='Load to database')
def load(job, dataset, source_name=None):
    """ Load the table artifact for this dataset into the fact
    table. """
    job.set_source(source_name)
    table = Table(job.package, ARTIFACT_NAME)
    dataset.fields = table.meta.get('fields', {})
    if not len(dataset.fields):
        raise ValueError('No columns recognized in source data.')

    db.session.commit()

    dataset.fact_table.drop()
    dataset.fact_table.create()
    dataset.fact_table.load_iter(table.records())
