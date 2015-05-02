import logging

from flask import Blueprint, request
from apikit import jsonify, Pager, obj_or_404
from loadkit import logger

from spendb.core import data_manager
from spendb.model import Run
from spendb.lib.helpers import get_dataset
from spendb.views.error import api_json_errors


log = logging.getLogger(__name__)
blueprint = Blueprint('runs_api3', __name__)


@blueprint.route('/datasets/<dataset>/runs')
@api_json_errors
def index(dataset):
    dataset = get_dataset(dataset)
    q = Run.all(dataset)
    if 'source' in request.args:
        q = q.filter(Run.source == request.args.get('source'))
    pager = Pager(q, dataset=dataset.name)
    return jsonify(pager)


@blueprint.route('/datasets/<dataset>/runs/<id>')
@api_json_errors
def view(dataset, id):
    dataset = get_dataset(dataset)
    run = obj_or_404(Run.by_id(dataset, id))
    data = run.to_dict()
    package = data_manager.package(dataset.name)
    data['messages'] = list(logger.load(package, run.id))
    return jsonify(data)
