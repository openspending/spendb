import logging
from flask import Flask
from flask import url_for as _url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.babel import Babel
from flask.ext.cache import Cache
from flask.ext.mail import Mail
from flask.ext.assets import Environment
from flask.ext.migrate import Migrate
from flask.ext.cors import CORS
from flask_flatpages import FlatPages
from celery import Celery
from cubes import Workspace, ext

from spendb import default_settings
from spendb.etl.manager import DataManager

logging.basicConfig(level=logging.DEBUG)

# specific loggers
logging.getLogger('cubes').setLevel(logging.WARNING)
logging.getLogger('markdown').setLevel(logging.WARNING)
logging.getLogger('boto').setLevel(logging.WARNING)
logging.getLogger('spendb.core.cors').setLevel(logging.WARNING)


db = SQLAlchemy()
babel = Babel()
login_manager = LoginManager()
cache = Cache()
mail = Mail()
assets = Environment()
migrate = Migrate()
pages = FlatPages()
data_manager = DataManager()
cors = CORS()


def create_app(**config):
    app = Flask(__name__, static_folder='../spendb.ui')
    app.config.from_object(default_settings)
    app.config.from_envvar('SPENDB_SETTINGS', silent=True)
    app.config.update(config)

    db.init_app(app)
    babel.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    assets.init_app(app)
    login_manager.init_app(app)
    data_manager.init_app(app)
    pages.init_app(app)
    migrate.init_app(app, db, directory=app.config.get('ALEMBIC_DIR'))
    cors.init_app(app, resources=r'/api/*', supports_credentials=True,
                  methods=['GET', 'HEAD', 'OPTIONS'])

    ws = Workspace()
    ext.model_provider("spending", metadata={})
    ext.store("spending")
    ws.register_default_store('spending', model_provider='spending')
    app.cubes_workspace = ws
    return app


def create_web_app(**config):
    app = create_app(**config)

    from spendb.assets import register_scripts
    register_scripts(app)

    from spendb.views import register_views
    register_views(app, babel)
    return app


def create_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery


def url_for(endpoint, **kwargs):
    try:
        from flask import current_app
        if current_app.config.get('PREFERRED_URL_SCHEME'):
            kwargs['_scheme'] = current_app.config.get('PREFERRED_URL_SCHEME')
        url = _url_for(endpoint, _external=True, **kwargs)
        return url
    except:
        return None
