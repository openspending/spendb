import argparse
import logging
import sys
import urllib2
import urlparse
import json

from colander import Invalid

from spendb.model import Dataset
from spendb.core import db
from spendb.validation.model import validate_model

log = logging.getLogger(__name__)


def _is_local_file(url):
    """ Check to see if the provided url is a local file. """
    parsed_result = urlparse.urlparse(url)
    return parsed_result.scheme in ['', 'file']


def json_of_url(url):
    if _is_local_file(url):
        url = url.replace('file://', '')
        return json.load(open(url, 'r'))
    else:
        return json.load(urllib2.urlopen(url))


def get_model(model):
    """ Get and validate the model. If the model doesn't validate
    we exit the program. """
    model = json_of_url(model)

    # Validate the model
    try:
        log.info("Validating model")
        model = validate_model(model)
    except Invalid as i:
        log.error("Errors occured during model validation:")
        for field, error in i.asdict().items():
            log.error("%s: %s", field, error)
        sys.exit(1)
    return model


def get_or_create_dataset(model):
    """ Based on a provided model we get the model (if it doesn't
    exist we create it). """
    dataset = Dataset.by_name(model['dataset']['name'])

    # If the dataset wasn't found we create it
    if dataset is None:
        dataset = Dataset(model)
        db.session.add(dataset)
        db.session.commit()

    log.info("Dataset: %s", dataset.name)
    return dataset
