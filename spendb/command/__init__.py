''' Interface to common administrative tasks for SpenDB. '''
import logging
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand

from spendb.core import create_web_app
from spendb.tasks import load_from_url
from spendb.command import db
from spendb.command.importer import get_or_create_dataset, get_model

log = logging.getLogger(__name__.split('.')[0])
app = create_web_app()
manager = Manager(app, description=__doc__)

manager.add_command('db', db.manager)
manager.add_command('alembic', MigrateCommand)


@manager.command
def grantadmin(username):
    """ Grant admin privileges to given user """
    from spendb.model import meta as db
    from spendb.model.account import Account

    account = Account.by_name(username)
    if account is None:
        raise Exception("Account `%s` not found." % username)

    account.admin = True
    db.session.add(account)
    db.session.commit()


@manager.option('-n', '--dry-run', dest='dry_run', action='store_true',
                help="Perform a dry run, don't load any data.")
@manager.option('-i', '--index', dest='build_indices', action='store_true',
                help="Suppress Solr index build.")
@manager.option('--max-lines', action="store", dest='max_lines', type=int,
                default=None, metavar='N',
                help="Number of lines to import.")
@manager.option('--raise-on-error', action="store_true",
                dest='raise_errors', default=False,
                help='Get full traceback on first error.')
@manager.option('--model', action="store", dest='model',
                default=None, metavar='url', required=True,
                help="URL of JSON format model (metadata and mapping).")
@manager.option('--visualisations', action="store", dest="views",
                default=None, metavar='url/file',
                help="URL/file of JSON format visualisations.")
@manager.option('data_url', help="Data file URL")
@manager.command
def csvimport(**args):
    """ Load a CSV dataset """
    model = get_model(args['model'])
    dataset = get_or_create_dataset(model)
    load_from_url(dataset, args['data_url'])


def main():
    manager.run()

if __name__ == "__main__":
    main()
