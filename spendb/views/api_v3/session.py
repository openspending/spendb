import logging

from flask import Blueprint
from flask.ext.login import current_user
from apikit import jsonify


log = logging.getLogger(__name__)
blueprint = Blueprint('sessions_api3', __name__)


@blueprint.route('/sessions')
def session():
    data = {
        'logged_in': current_user.is_authenticated(),
        'user': None
    }
    if current_user.is_authenticated():
        data['user'] = current_user
    return jsonify(data)
