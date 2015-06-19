from flask import Blueprint, render_template, request, redirect, current_app
from flask.ext.babel import gettext
from apikit import jsonify

from spendb.views.i18n import set_session_locale
from spendb.views.cache import disable_cache


blueprint = Blueprint('home', __name__)


@blueprint.route('/')
@blueprint.route('/datasets/new')
@blueprint.route('/login')
@blueprint.route('/settings')
@blueprint.route('/accounts/<account>')
@blueprint.route('/docs/<path:page>')
@blueprint.route('/datasets/<dataset>/admin/data')
@blueprint.route('/datasets/<dataset>/admin/metadata')
@blueprint.route('/datasets/<dataset>/admin/model')
@blueprint.route('/datasets/<dataset>/admin/runs/<run>')
def index(*a, **kw):
    from spendb.views.context import angular_templates
    return render_template('angular.html',
                           templates=angular_templates(current_app))


@blueprint.route('/set-locale', methods=['POST'])
def set_locale():
    disable_cache()
    locale = request.json.get('locale')

    if locale is not None:
        set_session_locale(locale)
    return jsonify({'locale': locale})


@blueprint.route('/favicon.ico')
def favicon():
    return redirect('/static/img/favicon.ico', code=301)


@blueprint.route('/__ping__')
def ping():
    disable_cache()
    from spendb.tasks import ping
    ping.delay()
    return jsonify({
        'status': 'ok',
        'message': gettext("Sent ping!")
    })
