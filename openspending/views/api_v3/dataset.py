import logging

from flask import Blueprint
from flask.ext.login import current_user
from restpager import Pager

from openspending.model import Dataset
from openspending.lib.jsonexport import jsonify

log = logging.getLogger(__name__)
blueprint = Blueprint('datasets_api3', __name__)


@blueprint.route('/datasets')
def index():
    q = Dataset.all_by_account(current_user)
    pager = Pager(q)
    return jsonify(pager)
