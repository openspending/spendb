import logging

from flask import Blueprint, request
from archivekit import Source
from werkzeug.exceptions import BadRequest
from apikit import jsonify, request_data

from spendb.core import data_manager, url_for
from spendb.auth import require
from spendb.lib.helpers import get_dataset
from spendb.views.error import api_json_errors
from spendb.tasks import load_from_url, load_from_source
from spendb.etl.tasks import extract_fileobj


log = logging.getLogger(__name__)
blueprint = Blueprint('sources_api3', __name__)


def source_to_dict(dataset, source):
    data = dict(source.meta.items())
    data.pop('http_headers', None)
    data['data_url'] = source.url
    data['api_url'] = url_for('sources_api3.view', dataset=dataset.name,
                              name=data.get('name'))
    return data


@blueprint.route('/datasets/<dataset>/sources')
@api_json_errors
def index(dataset):
    dataset = get_dataset(dataset)
    package = data_manager.package(dataset.name)
    sources = [source_to_dict(dataset, s) for s in package.all(Source)]
    sources = sorted(sources, key=lambda s: s['updated_at'], reverse=True)
    return jsonify({
        'results': sources[:10],
        'total': len(sources)
    })


@blueprint.route('/datasets/<dataset>/sources/upload', methods=['POST', 'PUT'])
@api_json_errors
def upload(dataset):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)
    file_ = request.files.get('file')
    if not file_ or not file_.filename:
        raise BadRequest("You need to upload a file")
    source = extract_fileobj(dataset, fh=file_, file_name=file_.filename)
    load_from_source.delay(dataset.name, source.name)
    return jsonify(source_to_dict(dataset, source))


@blueprint.route('/datasets/<dataset>/sources/submit', methods=['POST', 'PUT'])
@api_json_errors
def submit(dataset):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)
    data = request_data()
    if not data.get('url'):
        raise BadRequest("You need to submit a URL")
    load_from_url.delay(dataset.name, data.get('url'))
    return jsonify({'status': 'ok'})


@blueprint.route('/datasets/<dataset>/sources/<name>')
@api_json_errors
def view(dataset, name):
    dataset = get_dataset(dataset)
    package = data_manager.package(dataset.name)
    source = Source(package, name)
    return jsonify(source_to_dict(dataset, source))
