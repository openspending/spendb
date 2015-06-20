from flask import current_app, request
from flask.ext.babel import get_locale

from spendb import __version__
from spendb.core import url_for
from spendb.validation.common import RESERVED_TERMS
from spendb.views.cache import setup_caching, cache_response
from spendb.views.home import blueprint as home


@home.before_app_request
def before_request():
    request._return_json = False
    setup_caching()


@home.after_app_request
def after_request(resp):
    resp.headers['Server'] = 'SpenDB/%s' % __version__

    if resp.is_streamed and request.endpoint != 'static':
        # http://wiki.nginx.org/X-accel#X-Accel-Buffering
        resp.headers['X-Accel-Buffering'] = 'no'

    return cache_response(resp)


@home.app_context_processor
def template_context_processor():
    locale = get_locale()
    data = {
        'current_language': locale.language,
        'url_for': url_for,
        'reserved_terms': RESERVED_TERMS,
        'site_url': url_for('home.index').rstrip('/'),
        'number_symbols_group': locale.number_symbols.get('group'),
        'number_symbols_decimal': locale.number_symbols.get('decimal'),
        'site_title': current_app.config.get('SITE_TITLE')
    }
    return data
