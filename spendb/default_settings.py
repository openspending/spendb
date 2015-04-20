from kombu import Exchange, Queue

SECRET_KEY = 'foo'
DEBUG = True

SITE_TITLE = 'OpenSpending'

SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/openspending'
SOLR_URL = 'http://localhost:8983/solr'

BABEL_DEFAULT_LOCALE = 'en'

MAIL_SERVER = 'localhost'
# MAIL_PORT = 25
# MAIL_USE_TLS = False
# MAIL_USE_SSL = False
# MAIL_USERNAME = None
# MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = 'noreply@openspending.org'

CACHE = False
CACHE_TYPE = 'simple'

WIDGETS_BASE = '/static/openspendingjs/widgets/'
WIDGETS = ['treemap', 'bubbletree', 'aggregate_table']

# Worker queue configuration.
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# If you set ``EAGER``, processing will happen inline.
CELERY_ALWAYS_EAGER = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

CELERY_DEFAULT_QUEUE = 'loading'
CELERY_QUEUES = (
    Queue('indexing', Exchange('openspending'), routing_key='openspending'),
    Queue('loading', Exchange('openspending'), routing_key='openspending'),
)

CELERY_ROUTES = {
    'openspending.tasks.load_from_url': {
        'queue': 'loading'
    },
    'openspending.tasks.index_dataset': {
        'queue': 'indexing'
    },
}

MAX_CONTENT_LENGTH = 1024 * 1024 * 500  # 500 MB
