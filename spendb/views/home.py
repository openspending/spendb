from flask import Blueprint, render_template, request, redirect, flash
from flask.ext.babel import gettext
from apikit import jsonify

from spendb.core import pages
from spendb.views.i18n import set_session_locale
from spendb.views.api.dataset import query_index
from spendb.views.cache import disable_cache, etag_cache_keygen


blueprint = Blueprint('home', __name__)


@blueprint.route('/')
def index():
    page = pages.get_or_404('index')
    pager, _, territories = query_index()
    etag_cache_keygen(pager.cache_keys())
    return render_template('home/index.html', pager=pager,
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


@blueprint.route('/docs/<path:path>.html')
def page(path):
    page = pages.get_or_404(path)
    menu = [p for p in pages if not p['hidden']]
    template = page.meta.get('template', 'home/page.html')
    return render_template(template, page=page, pages=menu)
