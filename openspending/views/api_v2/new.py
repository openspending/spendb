import logging
import urllib2
import json

from flask import request
from flask.ext.login import current_user
from colander import Invalid

from openspending import auth as can
from openspending.core import db
from openspending.auth import require
from openspending.model.dataset import Dataset
from openspending.lib.jsonexport import jsonify
from openspending.lib.paramparser import LoadingAPIParamParser
from openspending.lib.hypermedia import dataset_apply_links
from openspending.tasks import load_from_url
from openspending.validation.model import validate_model
from openspending.views.api_v2.common import blueprint


log = logging.getLogger(__name__)


@blueprint.route('/api/2/new', methods=['POST'])
def create():
    """ Adds a new dataset dynamically through a POST request. """
    require.account.logged_in()

    # Parse the loading api parameters to get them into the right format
    parser = LoadingAPIParamParser(request.form)
    params, errors = parser.parse()

    if errors:
        return jsonify({'errors': errors}, status=400)

    # Precedence of budget data package over other methods
    if 'budget_data_package' in params:
        err = {'errors': 'BDP loading is disabled in 0.17'}
        return jsonify(err, status=400)
    
    # params['metadata'], params['csv_file'], params['private'])
    if params['metadata'] is None:
        return jsonify({'errors': 'metadata is missing'}, status=400)

    if params['csv_file'] is None:
        return jsonify({'errors': 'csv_file is missing'}, status=400)
        
    # We proceed with the dataset
    try:
        model = json.load(urllib2.urlopen(params['metadata']))
    except:
        return jsonify({'errors': 'JSON model could not be parsed'}, status=400)
    try:
        log.info("Validating model")
        model = validate_model(model)
    except Invalid as i:
        log.error("Errors occured during model validation:")
        for field, error in i.asdict().items():
            log.error("%s: %s", field, error)
        return jsonify({'errors': 'Model is not well formed'}, status=400)
    dataset = Dataset.by_name(model['dataset']['name'])
    if dataset is None:
        dataset = Dataset(model)
        require.dataset.create()
        dataset.managers.append(current_user)
        dataset.private = params['private']
        db.session.add(dataset)
    else:
        require.dataset.update(dataset)

    log.info("Dataset: %s", dataset.name)
    db.session.commit()

    # Send loading of source into celery queue
    load_from_url.delay(dataset.name, params['csv_file'])
    return jsonify(dataset_apply_links(dataset.as_dict()))


@blueprint.route('/api/2/permissions')
def permissions():
    """
    Check a user's permissions for a given dataset. This could also be
    done via request to the user, but since we're not really doing a
    RESTful service we do this via the api instead.
    """
    if 'dataset' not in request.args:
        return jsonify({'error': 'Parameter dataset missing'}, status=400)

    # Get the dataset we want to check permissions for
    dataset = Dataset.by_name(request.args['dataset'])

    # Return permissions
    return jsonify({
        'create': can.dataset.create() and dataset is None,
        'read': False if dataset is None else can.dataset.read(dataset),
        'update': False if dataset is None else can.dataset.update(dataset),
        'delete': False if dataset is None else can.dataset.delete(dataset)
    })
