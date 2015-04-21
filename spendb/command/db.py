import logging
import os

from flask import current_app
from flask.ext.migrate import upgrade

from spendb.core import db
from spendb.model import Dataset
from spendb.command.util import create_submanager
from spendb.command.util import CommandException

log = logging.getLogger(__name__)

manager = create_submanager(description='Database operations')


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
        raise CommandException("Dataset does not exist: '%s'" % name)
    dataset.drop()
    db.session.delete(dataset)
    db.session.commit()


@manager.command
def migrate():
    """ Run pending data migrations """
    upgrade()


@manager.command
def init():
    """ Initialize the database """
    migrate()


@manager.command
def modelmigrate():
    """ Run pending data model migrations """
    from spendb.validation.migration import migrate_model
    dataset = db.Table('dataset', db.metadata, autoload=True)
    rp = db.engine.execute(dataset.select())
    while True:
        ds = rp.fetchone()
        if ds is None:
            break
        log.info('Migrating %s...', ds['name'])
        model = migrate_model(ds['data'])
        version = model.get('dataset').get('schema_version')
        if 'dataset' in model:
            del model['dataset']
        q = dataset.update().where(dataset.c.id == ds['id'])
        q = q.values({'data': model, 'schema_version': version})
        db.engine.execute(q)
