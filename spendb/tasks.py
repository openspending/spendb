from celery.utils.log import get_task_logger

from openspending.core import create_app, create_celery
from openspending.model import Dataset
from openspending.etl import tasks


log = get_task_logger(__name__)

flask_app = create_app()
celery = create_celery(flask_app)


@celery.task(ignore_result=True)
def load_from_url(dataset_name, url):
    with flask_app.app_context():
        dataset = Dataset.by_name(dataset_name)
        source = tasks.extract_url(dataset, url)
        if source is None:
            return
        artifact = tasks.transform_source(dataset, source.name)
        if artifact is None:
            return
        tasks.load(dataset, source_name=source.name)


@celery.task(ignore_result=True)
def ping():
    with flask_app.app_context():
        log.info("Pong.")
