import logging

from flask import Blueprint
from flask.ext.login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash
from flask.ext.babel import gettext as _
from apikit import jsonify, request_data

from spendb.core import login_manager
from spendb.model import Account
from spendb.views.cache import disable_cache

log = logging.getLogger(__name__)
blueprint = Blueprint('sessions_api', __name__)


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.args.get('api_key')
    if api_key and len(api_key):
        account = Account.by_api_key(api_key)
        if account:
            return account

    api_key = request.headers.get('Authorization')
    if api_key and len(api_key) and ' ' in api_key:
        method, api_key = api_key.split(' ', 1)
        if method.lower() == 'apikey':
            account = Account.by_api_key(api_key)
            if account:
                return account
    return None


@blueprint.route('/sessions')
def session():
    data = {
        'logged_in': current_user.is_authenticated(),
        'user': None
    }
    if current_user.is_authenticated():
        data['user'] = current_user
    return jsonify(data)


@blueprint.route('/sessions/login', methods=['POST', 'PUT'])
def login():
    data = request_data()
    account = Account.by_name(data.get('login'))
    if account is not None:
        if check_password_hash(account.password, data.get('password')):
            login_user(account, remember=True)
            return jsonify({
                'status': 'ok',
                'message': _("Welcome back, %(name)s!", name=account.name)
            })
    return jsonify({
        'status': 'error',
        'message': _("Incorrect user name or password!")
    }, status=400)


@blueprint.route('/sessions/logout', methods=['POST', 'PUT'])
def logout():
    disable_cache()
    logout_user()
    return jsonify({
        'status': 'ok',
        'message': _("You have been logged out.")
    })
