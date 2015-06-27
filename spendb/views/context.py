from flask import current_app, request, session, get_flashed_messages
from flask.ext.login import current_user
from babel import Locale
from apikit import cache_hash

from spendb import __version__
from spendb.core import babel
from spendb.views.error import NotModified
from spendb.views.home import blueprint as home


def get_locale():
    if 'locale' in session:
        return Locale.parse(session.get('locale'))
    else:
        requested = request.accept_languages.values()
        requested = [l.replace('-', '_') for l in requested]
        available = map(unicode, babel.list_translations())
        return Locale.negotiate(available, requested)


@home.before_app_request
def before_request():
    current_app.cubes_workspace.flush_lookup_cache()
    request._http_etag = None
    request._http_private = False


@home.after_app_request
def after_request(resp):
    resp.headers['Server'] = 'SpenDB/%s' % __version__

    if resp.is_streamed and request.endpoint != 'static':
        # http://wiki.nginx.org/X-accel#X-Accel-Buffering
        resp.headers['X-Accel-Buffering'] = 'no'

    if request.endpoint == 'static':
        resp.cache_control.max_age = 3600 * 6
        resp.cache_control.public = True
        return resp

    # skip cache under these conditions:
    if not current_app.config.get('CACHE') \
            or request.method not in ['GET', 'HEAD', 'OPTIONS'] \
            or resp.status_code > 399 \
            or resp.is_streamed \
            or request._http_etag is None:
        resp.cache_control.no_cache = True
        return resp

    if not request._http_private:
        resp.cache_control.public = True
    else:
        resp.cache_control.private = True
    resp.cache_control.max_age = 3600 * 6
    resp.cache_control.must_revalidate = True
    resp.set_etag(request._http_etag)
    return resp


def etag_cache_keygen(key_obj, private=False):
    request._http_private = private

    args = sorted(set(request.args.items()))
    # jquery where is your god now?!?
    args = filter(lambda (k, v): k != '_', args)

    request._http_etag = cache_hash(args, current_user,
                                    key_obj, get_locale())
    if request.if_none_match == request._http_etag:
        raise NotModified()
