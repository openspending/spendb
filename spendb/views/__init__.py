from cubes.server import slicer
from colander import Invalid

from spendb.lib import filters

from spendb.views.context import home
from spendb.views.cache import NotModified, handle_not_modified
from spendb.views.i18n import get_locale

from spendb.views.account import blueprint as account
from spendb.views.dataset import blueprint as dataset
from spendb.views.error import handle_error, handle_invalid
from spendb.views.api_v3.dataset import blueprint as datasets_v3
from spendb.views.api_v3.meta import blueprint as meta_v3
from spendb.views.api_v3.session import blueprint as session_v3
from spendb.views.api_v3.source import blueprint as source_v3
from spendb.views.api_v3.run import blueprint as run_v3


def register_views(app, babel):
    babel.locale_selector_func = get_locale

    app.register_blueprint(meta_v3, url_prefix='/api/3')
    app.register_blueprint(session_v3, url_prefix='/api/3')
    app.register_blueprint(run_v3, url_prefix='/api/3')
    app.register_blueprint(source_v3, url_prefix='/api/3')
    app.register_blueprint(datasets_v3, url_prefix='/api/3')

    # expose ``cubes``:
    app.register_blueprint(slicer, url_prefix='/api/slicer', config={})

    app.register_blueprint(home)
    app.register_blueprint(account)
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
