from celery.utils.log import get_task_logger

from spendb.core import create_app, create_celery
from spendb.model import Dataset
from spendb.etl import tasks


log = get_task_logger(__name__)

flask_app = create_app()
celery = create_celery(flask_app)


@celery.task(ignore_result=True)
def load_from_url(dataset_name, url):
    with flask_app.app_context():
        dataset = Dataset.by_name(dataset_name)
        if dataset is None:
            log.error("Dataset not found: %s", dataset_name)
            return
        source = tasks.extract_url(dataset, url)
        if source is not None:
            load_from_source.delay(dataset_name, source.name)


@celery.task(ignore_result=True)
def load_from_source(dataset_name, source_name):
    with flask_app.app_context():
        dataset = Dataset.by_name(dataset_name)
        if dataset is None:
            log.error("Dataset not found: %s", dataset_name)
            return
        if source_name is None:
            log.error("No source specified: %s", dataset_name)
            return
        artifact = tasks.transform_source(dataset, source_name)
        if artifact is None:
            return
        tasks.load(dataset, source_name=source_name)


@celery.task(ignore_result=True)
def ping():
    with flask_app.app_context():
        log.info("Pong.")
