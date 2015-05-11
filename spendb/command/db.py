import logging

from flask.ext.migrate import upgrade
from flask.ext.script import Manager

from spendb.core import db
from spendb.model import Dataset

log = logging.getLogger(__name__)

manager = Manager()
manager.__doc__ = 'Database operations'


@manager.command
def drop():
    """ Drop database """
    log.warn("Dropping database")
    db.metadata.reflect()
    db.metadata.drop_all()


@manager.command
def drop_dataset(name):
    """ Drop a dataset from the database """
    log.warn("Dropping dataset '%s'", name)
    dataset = db.session.query(Dataset).filter_by(name=name).first()
    if dataset is None:
        raise Exception("Dataset does not exist: '%s'" % name)
    dataset.drop()
    db.session.delete(dataset)
    db.session.commit()


@manager.command
def migrate():
    """ Initialize or upgrade the database """
    upgrade()
