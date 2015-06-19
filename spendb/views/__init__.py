from cubes.server import slicer
from colander import Invalid

from spendb.lib import filters

from spendb.views.context import home
from spendb.views.cache import NotModified, handle_not_modified
from spendb.views.i18n import get_locale

from spendb.views.dataset import blueprint as dataset
from spendb.views.error import handle_error, handle_invalid
from spendb.views.api.dataset import blueprint as datasets_api
from spendb.views.api.meta import blueprint as meta_api
from spendb.views.api.session import blueprint as session_api
from spendb.views.api.source import blueprint as source_api
from spendb.views.api.run import blueprint as run_api
from spendb.views.api.account import blueprint as account_api


def register_views(app, babel):
    babel.locale_selector_func = get_locale

    app.register_blueprint(meta_api, url_prefix='/api/3')
    app.register_blueprint(session_api, url_prefix='/api/3')
    app.register_blueprint(run_api, url_prefix='/api/3')
    app.register_blueprint(source_api, url_prefix='/api/3')
    app.register_blueprint(datasets_api, url_prefix='/api/3')
    app.register_blueprint(account_api, url_prefix='/api/3')

    # expose ``cubes``:
    app.register_blueprint(slicer, url_prefix='/api/slicer', config={})

    app.register_blueprint(home)
    app.register_blueprint(dataset)

    app.error_handler_spec[None][400] = handle_error
    app.error_handler_spec[None][401] = handle_error
    app.error_handler_spec[None][402] = handle_error
    app.error_handler_spec[None][403] = handle_error
    app.error_handler_spec[None][404] = handle_error
    app.error_handler_spec[None][500] = handle_error

    custom = (
        (Invalid, handle_invalid),
        (NotModified, handle_not_modified)
    )
    app.error_handler_spec[None][None] = custom

    app.jinja_env.filters.update({
        'markdown_preview': filters.markdown_preview,
        'markdown': filters.markdown,
        'format_date': filters.format_date,
        'readable_url': filters.readable_url
    })
