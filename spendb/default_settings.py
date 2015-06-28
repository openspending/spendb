import os

SECRET_KEY = 'foo'
DEBUG = True

SITE_TITLE = 'SpenDB'

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/spendb'

BABEL_DEFAULT_LOCALE = 'en'

MAIL_SERVER = 'localhost'
# MAIL_PORT = 25
# MAIL_USE_TLS = False
# MAIL_USE_SSL = False
# MAIL_USERNAME = None
# MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = 'noreply@mapthemoney.org'

CACHE = False
CACHE_TYPE = 'simple'

PREFERRED_URL_SCHEME = 'http'

ALEMBIC_DIR = os.path.join(os.path.dirname(__file__), 'migrate')
ALEMBIC_DIR = os.path.abspath(ALEMBIC_DIR)

FLATPAGES_ROOT = os.path.join(os.path.dirname(__file__), '..', 'pages')
FLATPAGES_ROOT = os.path.abspath(FLATPAGES_ROOT)

# Worker queue configuration.
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# If you set ``EAGER``, processing will happen inline.
CELERY_ALWAYS_EAGER = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# CELERY_DEFAULT_QUEUE = 'loading'
# CELERY_QUEUES = (
#     Queue('indexing', Exchange('spendb'), routing_key='spendb'),
#     Queue('loading', Exchange('spendb'), routing_key='spendb'),
# )

# CELERY_ROUTES = {
#     'spendb.tasks.load_from_url': {
#         'queue': 'loading'
#     },
#     'spendb.tasks.index_dataset': {
#         'queue': 'indexing'
#     },
# }
