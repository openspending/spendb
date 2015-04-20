import argparse
import logging
import sys
import urllib2
import urlparse
import json

from colander import Invalid

from spendb.model import Dataset, Account
from spendb.core import db
from spendb.tasks import load_from_url
from spendb.validation.model import validate_model

log = logging.getLogger(__name__)

SHELL_USER = 'system'


def shell_account():
    account = Account.by_name(SHELL_USER)
    if account is not None:
        return account
    account = Account()
    account.name = SHELL_USER
    db.session.add(account)
    return account


def _is_local_file(url):
    """
    Check to see if the provided url is a local file. Returns True if it is
    and False if it isn't. This method only checks if their is a scheme
    associated with the url or not (so file:location will be regarded as a url)
    """

    # Parse the url and check if scheme is '' (no scheme)
    parsed_result = urlparse.urlparse(url)
    return parsed_result.scheme == ''


def json_of_url(url):
    # Check if it's a local file
    if _is_local_file(url):
        # If it is we open it as a normal file
        return json.load(open(url, 'r'))
    else:
        # If it isn't we open the url as a file
        return json.load(urllib2.urlopen(url))


def get_model(model):
    """
    Get and validate the model. If the model doesn't validate we exit the
    program.
    """

    # Get and parse the model
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

    # Return the model
    return model


def get_or_create_dataset(model):
    """
    Based on a provided model we get the model (if it doesn't exist we
    create it).
    """

    # Get the dataset by the name provided in the model
    dataset = Dataset.by_name(model['dataset']['name'])

    # If the dataset wasn't found we create it
    if dataset is None:
        dataset = Dataset(model)
        db.session.add(dataset)
        db.session.commit()

    # Log information about the dataset and return it
    log.info("Dataset: %s", dataset.name)
    return dataset


def add_import_commands(manager):

    @manager.option('-n', '--dry-run', dest='dry_run', action='store_true',
                    help="Perform a dry run, don't load any data.")
    @manager.option('-i', '--index', dest='build_indices', action='store_true',
                    help="Suppress Solr index build.")
    @manager.option('--max-lines', action="store", dest='max_lines', type=int,
                    default=None, metavar='N',
                    help="Number of lines to import.")
    @manager.option('--raise-on-error', action="store_true",
                    dest='raise_errors', default=False,
                    help='Get full traceback on first error.')
    @manager.option('--model', action="store", dest='model',
                    default=None, metavar='url', required=True,
                    help="URL of JSON format model (metadata and mapping).")
    @manager.option('--visualisations', action="store", dest="views",
                    default=None, metavar='url/file',
                    help="URL/file of JSON format visualisations.")
    @manager.option('dataset_urls', nargs=argparse.REMAINDER,
                    help="Dataset file URLs")
    @manager.command
    def csvimport(**args):
        """ Load a CSV dataset """
        # Get the model
        model = get_model(args['model'])

        # Get the dataset for the model
        dataset = get_or_create_dataset(model)

        # For every url in mapped dataset_urls (arguments) we import it
        for url in args['dataset_urls']:
            load_from_url(dataset, url)
