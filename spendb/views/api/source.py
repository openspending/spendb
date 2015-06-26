import logging
from StringIO import StringIO

from flask import Blueprint, request, redirect, send_file
from archivekit import Source
from werkzeug.exceptions import BadRequest
from apikit import jsonify, Pager, request_data

from spendb.core import data_manager, url_for
from spendb.auth import require
from spendb.lib.helpers import get_dataset
from spendb.views.cache import disable_cache
from spendb.tasks import load_from_url, load_from_source
from spendb.etl.tasks import extract_fileobj
from spendb.etl.upload import generate_s3_upload_policy


log = logging.getLogger(__name__)
blueprint = Blueprint('sources_api', __name__)


def source_to_dict(dataset, source):
    data = dict(source.meta.items())
    data.pop('http_headers', None)
    data['data_url'] = url_for('sources_api.serve', dataset=dataset.name,
                               name=source.name)
    data['runs_url'] = url_for('runs_api.index', dataset=dataset.name,
                               source=source.name)
    data['api_url'] = url_for('sources_api.view', dataset=dataset.name,
                              name=source.name)
    return data


@blueprint.route('/datasets/<dataset>/sources')
def index(dataset):
    disable_cache()
    dataset = get_dataset(dataset)
    package = data_manager.package(dataset.name)
    sources = list(package.all(Source))
    sources = sorted(sources, key=lambda s: s.meta.get('updated_at'),
                     reverse=True)
    rc = lambda ss: [source_to_dict(dataset, s) for s in ss]
    return jsonify(Pager(sources, dataset=dataset.name, limit=5,
                   results_converter=rc))


@blueprint.route('/datasets/<dataset>/sources/upload', methods=['POST', 'PUT'])
def upload(dataset):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)
    file_ = request.files.get('file')
    if not file_ or not file_.filename:
        raise BadRequest("You need to upload a file")
    # TODO: consider copying this into a tempfile before upload to make
    # boto happy (it appears to be whacky in it's handling of flask uploads)
    source = extract_fileobj(dataset, fh=file_, file_name=file_.filename)
    load_from_source.delay(dataset.name, source.name)
    return jsonify(source_to_dict(dataset, source))


@blueprint.route('/datasets/<dataset>/sources/sign', methods=['POST', 'PUT'])
def sign(dataset):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)
    data = request_data()
    if not data.get('file_name'):
        raise BadRequest("You need to give a file name")
    data['mime_type'] = data.get('mime_type') or 'application/octet-stream'
    # create a stub:
    source = extract_fileobj(dataset, fh=StringIO(),
                             file_name=data['file_name'],
                             mime_type=data['mime_type'])

    # generate a policy document to replace with actual content:
    res = generate_s3_upload_policy(source, data['file_name'],
                                    data['mime_type'])
    return jsonify(res)


@blueprint.route('/datasets/<dataset>/sources/submit', methods=['POST', 'PUT'])
def submit(dataset):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)
    data = request_data()
    if not data.get('url'):
        raise BadRequest("You need to submit a URL")
    load_from_url.delay(dataset.name, data.get('url'))
    return jsonify({'status': 'ok'})


@blueprint.route('/datasets/<dataset>/sources/<name>')
def view(dataset, name):
    dataset = get_dataset(dataset)
    package = data_manager.package(dataset.name)
    source = Source(package, name)
    return jsonify(source_to_dict(dataset, source))


@blueprint.route('/datasets/<dataset>/serve/<name>')
def serve(dataset, name):
    dataset = get_dataset(dataset)
    package = data_manager.package(dataset.name)
    source = Source(package, name)
    if source.url is not None:
        return redirect(source.url)
    return send_file(source.fh(),
                     mimetype=source.meta.get('mime_type'))


@blueprint.route('/datasets/<dataset>/sources/load/<name>',
                 methods=['POST', 'PUT'])
def load(dataset, name):
    dataset = get_dataset(dataset)
    require.dataset.update(dataset)
    package = data_manager.package(dataset.name)
    source = Source(package, name)
    if not source.exists():
        raise BadRequest('Source does not exist.')
    load_from_source.delay(dataset.name, source.name)
    return jsonify({'status': 'ok'})
