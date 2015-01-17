import logging

from flask import Blueprint, request
from flask.ext.login import current_user
from flask.ext.babel import gettext as _
from colander import SchemaNode, String, Invalid
from restpager import Pager

from openspending.core import db
from openspending.model import Dataset
from openspending.auth import require
from openspending.lib import solr_util as solr
from openspending.lib.jsonexport import jsonify
from openspending.lib.helpers import url_for, get_dataset
from openspending.lib.indices import clear_index_cache
from openspending.views.cache import etag_cache_keygen
from openspending.views.context import api_form_data
from openspending.views.error import api_json_errors
from openspending.validation.dataset import dataset_schema
from openspending.validation.common import ValidationState


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
    dataset = api_form_data()
    schema = dataset_schema(ValidationState({'dataset': dataset}))
    data = schema.deserialize(dataset)
    if Dataset.by_name(data['name']) is not None:
        raise Invalid(SchemaNode(String(), name='dataset.name'),
                      _("A dataset with this identifer already exists!"))
    dataset = Dataset({'dataset': data})
    dataset.managers.append(current_user)
    db.session.add(dataset)
    db.session.commit()
    clear_index_cache()
    return view(dataset.name)


@blueprint.route('/datasets/<name>', methods=['POST', 'PUT'])
@api_json_errors
def update(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)
    schema = dataset_schema(ValidationState(dataset.model_data))
    data = schema.deserialize(api_form_data())
    dataset.update(data)
    db.session.commit()
    clear_index_cache()
    return view(name)


@blueprint.route('/datasets/<name>', methods=['DELETE'])
@api_json_errors
def delete(name):
    dataset = get_dataset(name)
    require.dataset.update(dataset)

    dataset.fact_table.drop()
    db.session.delete(dataset)
    db.session.commit()
    clear_index_cache()
    solr.drop_index(dataset.name)
    return jsonify({'status': 'deleted'}, status=410)
