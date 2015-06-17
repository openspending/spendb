import logging

from flask import Blueprint, request
from flask.ext.login import current_user
from flask.ext.babel import gettext as _
from colander import SchemaNode, String, Invalid
from sqlalchemy.orm import aliased
from apikit import jsonify, Pager, request_data
from fiscalmodel import COUNTRIES, LANGUAGES

from spendb.core import db
from spendb.model import Dataset, DatasetLanguage, DatasetTerritory
from spendb.auth import require
from spendb.lib.helpers import get_dataset
from spendb.views.cache import etag_cache_keygen
from spendb.views.error import api_json_errors
from spendb.validation.dataset import validate_dataset, validate_managers
from spendb.validation.model import validate_model


log = logging.getLogger(__name__)
blueprint = Blueprint('datasets_api', __name__)


def query_index():
    q = Dataset.all_by_account(current_user, order=False)
    q = q.order_by(Dataset.updated_at.desc())

    # Filter by languages if they have been provided
    for language in request.args.getlist('languages'):
        l = aliased(DatasetLanguage)
        q = q.join(l, Dataset._languages)
        q = q.filter(l.code == language)

    # Filter by territories if they have been provided
    for territory in request.args.getlist('territories'):
        t = aliased(DatasetTerritory)
        q = q.join(t, Dataset._territories)
        q = q.filter(t.code == territory)

    # Return a list of languages as dicts with code, count, url and label
    languages = [{'code': code, 'count': count, 'label': LANGUAGES.get(code)}
                 for (code, count) in DatasetLanguage.dataset_counts(q)]

    territories = [{'code': code, 'count': count, 'label': COUNTRIES.get(code)}
                   for (code, count) in DatasetTerritory.dataset_counts(q)]

    pager = Pager(q, limit=15)
    return pager, languages, territories


@blueprint.route('/datasets')
@api_json_errors
def index():
    pager, languages, territories = query_index()
    data = pager.to_dict()
    data['languages'] = languages
    data['territories'] = territories
    return jsonify(data)


@blueprint.route('/datasets/<name>')
@api_json_errors
def view(name):
    dataset = get_dataset(name)
    etag_cache_keygen(dataset)
    return jsonify(dataset)


@blueprint.route('/datasets', methods=['POST', 'PUT'])
@api_json_errors
def create():
    require.dataset.create()
    dataset = request_data()
    data = validate_dataset(dataset)
    if Dataset.by_name(data['name']) is not None:
        raise Invalid(SchemaNode(String(), name='name'),
                      _("A dataset with this identifer already exists!"))
    dataset = Dataset({'dataset': data, 'model': {}})
    dataset.managers.append(current_user)
    db.session.add(dataset)
    db.session.commit()
    return view(dataset.name)


@blueprint.route('/datasets/<name>', methods=['POST', 'PUT'])
@api_json_errors
def update(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)
    dataset.update(validate_dataset(request_data()))
    dataset.touch()
    db.session.commit()
    return view(name)


@blueprint.route('/datasets/<name>/structure')
@api_json_errors
def structure(name):
    dataset = get_dataset(name)
    etag_cache_keygen(dataset)
    return jsonify({
        'fields': dataset.fields,
        'samples': dataset.samples
    })


@blueprint.route('/datasets/<name>/model')
@api_json_errors
def model(name):
    dataset = get_dataset(name)
    etag_cache_keygen(dataset)
    return jsonify(dataset.model_data)


@blueprint.route('/datasets/<name>/model', methods=['POST', 'PUT'])
@api_json_errors
def update_model(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)
    model_data = validate_model(request_data())
    dataset.update_model(model_data)
    dataset.touch()
    db.session.commit()
    return model(name)


@blueprint.route('/datasets/<name>/managers')
@api_json_errors
def managers(name):
    dataset = get_dataset(name)
    etag_cache_keygen(dataset)
    return jsonify({'managers': dataset.managers})


@blueprint.route('/datasets/<name>/managers', methods=['POST', 'PUT'])
@api_json_errors
def update_managers(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)
    data = validate_managers(request_data())
    if current_user not in data['managers']:
        data['managers'].append(current_user)
    dataset.managers = data['managers']
    dataset.touch()
    db.session.commit()
    return managers(name)


@blueprint.route('/datasets/<name>', methods=['DELETE'])
@api_json_errors
def delete(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)

    dataset.flush()
    dataset.fact_table.drop()
    db.session.delete(dataset)
    db.session.commit()
    return jsonify({'status': 'deleted'}, status=410)
