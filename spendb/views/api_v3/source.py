import logging

from flask import Blueprint
from apikit import jsonify, request_data

from spendb.lib.helpers import get_dataset
from spendb.views.error import api_json_errors


log = logging.getLogger(__name__)
blueprint = Blueprint('datasets_api3', __name__)


@blueprint.route('/datasets/<dataset>/sources')
@api_json_errors
def index(dataset):
    dataset = get_dataset(dataset)
    pass
