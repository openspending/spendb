import os

from flask import current_app, request
from flask.ext.babel import get_locale
from flask.ext.login import current_user

from spendb import auth, __version__
from spendb.core import url_for
from spendb.validation.common import RESERVED_TERMS
from spendb.views.i18n import get_available_locales
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


def angular_templates(app):
    """ Find all angular templates and make them available in a variable
    which can be included in a Jinja template so that angular can load
    templates without doing a server round trip. """
    partials_dir = os.path.join(app.static_folder, 'templates')
    for (root, dirs, files) in os.walk(partials_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'rb') as fh:
                file_name = file_path[len(partials_dir) + 1:]
                yield (file_name, fh.read().decode('utf-8'))


def languages():
    current_locale = get_locale()

    def details(locale):
        return {
            "lang_code": locale.language,
            "lang_name": locale.language_name,
            "current_locale": locale == current_locale
        }
    return [details(l) for l in get_available_locales()]


@home.app_context_processor
def template_context_processor():
    locale = get_locale()
    data = {
        'DEBUG': current_app.config.get('DEBUG'),
        'current_language': locale.language,
        'current_locale': get_locale(),
        'reserved_terms': RESERVED_TERMS,
        'url_for': url_for,
        'site_url': url_for('home.index').rstrip('/'),
        'number_symbols_group': locale.number_symbols.get('group'),
        'number_symbols_decimal': locale.number_symbols.get('decimal'),
        'site_title': current_app.config.get('SITE_TITLE'),
        'languages': languages(),
        'logged_in': auth.account.logged_in(),
        'current_user': current_user,
        'can': auth
    }
    return data
