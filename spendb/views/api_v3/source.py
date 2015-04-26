import logging

from flask import Blueprint
from archivekit import Source
from apikit import jsonify, request_data

from spendb.core import data_manager
from spendb.lib.helpers import get_dataset
from spendb.views.error import api_json_errors


log = logging.getLogger(__name__)
blueprint = Blueprint('sources_api3', __name__)


@blueprint.route('/datasets/<dataset>/sources')
@api_json_errors
def index(dataset):
    dataset = get_dataset(dataset)
    package = data_manager.package(dataset.name)
    sources = list(package.all(Source))
    return jsonify({
        'results': sources,
        'total': len(sources)
    })
