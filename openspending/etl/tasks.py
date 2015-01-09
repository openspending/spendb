from loadkit import extract, transform, Source

from openspending.core import data_manager

ARTIFACT_NAME = 'table.json'


def extract_fileobj(dataset, fh, file_name=None):
    """ Upload contents of an opened fh to the data repository. """
    package = data_manager.package(dataset.name)
    source = extract.from_fileobj(package, fh, source_name=file_name)
    return source
    

def extract_url(dataset, url):
    """ Upload contents of a URL to the data repository. """
    package = data_manager.package(dataset.name)
    source = extract.from_url(package, url)
    return source
    

def transform_source(dataset, source_name):
    """ Transform the contents of an uploaded source dataset to a
    well-understood file format. """
    package = data_manager.package(dataset.name)
    source = Source(package, source_name)
    artifact = transform.to_table(source, ARTIFACT_NAME)
    return artifact

