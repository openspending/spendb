import logging
from functools import wraps
from datetime import datetime

from loadkit import Source
from loadkit.logfile import capture

from openspending.core import data_manager, db
from openspending.model.run import Run


class Job(object):
    
    def __init__(self, dataset, operation):
        self.log = logging.getLogger('openspending.etl')
        self.dataset = dataset
        self.operation = operation
        self.run = None

    def start(self):
        self.run = Run(self.operation, Run.STATUS_RUNNING, self.dataset)
        db.session.add(self.run)
        db.session.commit()

        self.package = data_manager.package(self.dataset.name)
        modules = [self.log, 'loadkit']
        self.log_handler = capture(self.package, self.run.id, modules)
        self.log.info("Starting: %s", self.operation)

    def set_source(self, source):
        if isinstance(source, Source):
            source = source.name
        self.run.source = source
        db.session.commit()

    def end(self, status):
        if not self.running:
            return
        self.run.status = status
        self.run.time_end = datetime.utcnow()
        self.dataset.touch()
        db.session.commit()
        self.log_handler.archive()

    @property
    def running(self):
        return self.run and self.run.status == Run.STATUS_RUNNING

    def complete(self):
        if self.running:
            self.log.info("Completed: %s", self.operation)
        self.end(Run.STATUS_COMPLETE)

    def failed(self):
        if self.running:
            self.log.warn("Failed: %s", self.operation)
        self.end(Run.STATUS_FAILED)


def job(operation=None):
    """ Wrap an ETL job. This will handle logging, run management
    and other tasks. It assumes the first positional argument is
    the dataset that this operation is performed on, and will
    inject another argument before that, the ``job``. """

    def decorator(fn):
        @wraps(fn)
        def wrapper(dataset, *a, **kw):
            job = Job(dataset, operation or fn.__name__)
            try:
                job.start()
                result = fn(job, dataset, *a, **kw)
                job.complete()
                return result
            except Exception, e:
                job.log.exception(e)
                job.failed()
            finally:
                if job.running:
                    job.failed()
        return wrapper

    return decorator
