from sqlalchemy import *
from migrate import *

meta = MetaData()


def upgrade(migrate_engine):
    print "WARNING: THIS MIGRATION IS TEMPORARY AND WILL EAT DATA"
    meta.bind = migrate_engine
    log_record = Table('log_record', meta, autoload=True)
    log_record.drop()
    run = Table('run', meta, autoload=True)
    run.c.source_id.drop()
    run_source = Column('source', Unicode)
    run_source.create(run)
    source = Table('source', meta, autoload=True)
    source.drop()
    ds = Table('dataset', meta, autoload=True)
    ds.c.ckan_uri.drop()
    ds.c.entry_custom_html.drop()
    ds.c.serp_title.drop()
    ds.c.serp_teaser.drop()


def downgrade(migrate_engine):
    raise NotImplementedError()
