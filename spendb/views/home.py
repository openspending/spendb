from flask import Blueprint, render_template, request, redirect, flash
from flask.ext.login import current_user
from flask.ext.babel import gettext
from apikit import jsonify

from spendb.core import pages
from spendb.views.i18n import set_session_locale
from spendb.model.dataset import Dataset, DatasetTerritory
from spendb.views.cache import disable_cache


blueprint = Blueprint('home', __name__)


@blueprint.route('/')
def index():
    page = pages.get_or_404('index')
    datasets = Dataset.all_by_account(current_user)
    territories = DatasetTerritory.dataset_counts(datasets)
    return render_template('home/index.html', datasets=datasets,
                           territories=territories, page=page)


@blueprint.route('/set-locale', methods=['POST'])
def set_locale():
    disable_cache()
    locale = request.json.get('locale')

    if locale is not None:
        set_session_locale(locale)
    return jsonify({'locale': locale})


@blueprint.route('/__version__')
def version():
    from spendb._version import __version__
    return __version__


@blueprint.route('/favicon.ico')
def favicon():
    return redirect('/static/img/favicon.ico', code=301)


@blueprint.route('/__ping__')
def ping():
    disable_cache()
    from spendb.tasks import ping
    ping.delay()
    flash(gettext("Sent ping!"), 'success')
    return redirect('/')


@blueprint.route('/<path:path>')
def page(path):
    page = pages.get_or_404(path)
    template = page.meta.get('template', 'page.html')
    return render_template(template, page=page)
