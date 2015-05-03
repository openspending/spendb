import logging

from flask import Blueprint
from flask.ext.login import current_user
from flask.ext.babel import gettext as _
from colander import SchemaNode, String, Invalid
from apikit import jsonify, Pager, request_data

from spendb.core import db
from spendb.model import Dataset
from spendb.auth import require
from spendb.lib.helpers import get_dataset
from spendb.views.cache import etag_cache_keygen
from spendb.views.error import api_json_errors
from spendb.validation.dataset import dataset_schema
from spendb.validation.mapping import mapping_schema
from spendb.validation.common import ValidationState


log = logging.getLogger(__name__)
blueprint = Blueprint('datasets_api3', __name__)




@blueprint.route('/datasets')
@api_json_errors
def index():
    q = Dataset.all_by_account(current_user)
    # TODO: Facets for territories and languages
    # TODO: filters on facet dimensions
    pager = Pager(q)
    return jsonify(pager)


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
    schema = dataset_schema(ValidationState({'dataset': dataset}))
    data = schema.deserialize(dataset)
    if Dataset.by_name(data['name']) is not None:
        raise Invalid(SchemaNode(String(), name='name'),
                      _("A dataset with this identifer already exists!"))
    dataset = Dataset({'dataset': data})
    dataset.managers.append(current_user)
    db.session.add(dataset)
    db.session.commit()
    return view(dataset.name)


@blueprint.route('/datasets/<name>', methods=['POST', 'PUT'])
@api_json_errors
def update(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)
    schema = dataset_schema(ValidationState(dataset.model_data))
    data = schema.deserialize(request_data())
    dataset.update(data)
    db.session.commit()
    return view(name)


@blueprint.route('/datasets/<name>/fields')
@api_json_errors
def fields(name):
    dataset = get_dataset(name)
    etag_cache_keygen(dataset)
    return jsonify(dataset.fields)


@blueprint.route('/datasets/<name>/model')
@api_json_errors
def model(name):
    dataset = get_dataset(name)
    etag_cache_keygen(dataset)
    return jsonify(dataset.mapping)


@blueprint.route('/datasets/<name>/model', methods=['POST', 'PUT'])
@api_json_errors
def update_model(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)
    model_data = dataset.model_data
    model_data['mapping'] = request_data()
    schema = mapping_schema(ValidationState(model_data))
    new_mapping = schema.deserialize(model_data['mapping'])
    dataset.data['mapping'] = new_mapping
    db.session.commit()
    return model(name)


@blueprint.route('/datasets/<name>', methods=['DELETE'])
@api_json_errors
def delete(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)

    dataset.fact_table.drop()
    db.session.delete(dataset)
    db.session.commit()
    return jsonify({'status': 'deleted'}, status=410)
