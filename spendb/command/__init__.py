''' Interface to common administrative tasks for SpenDB. '''
import logging
from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from spendb.core import create_web_app
from spendb.assets import assets
from spendb.command import user, db, importer

log = logging.getLogger(__name__.split('.')[0])

manager = Manager(create_web_app, description=__doc__)

manager.add_option('-v', '--verbose',
                   dest='verbose', action='append_const', const=1,
                   help='Increase the logging level')
manager.add_option('-q', '--quiet',
                   dest='verbose', action='append_const', const=-1,
                   help='Decrease the logging level')

manager.add_command('user', user.manager)
manager.add_command('db', db.manager)
manager.add_command('assets', ManageAssets(assets))

importer.add_import_commands(manager)


def main():
    manager.set_defaults()
    parser = manager.create_parser('ostool')
    args = parser.parse_args()
    args.verbose = 0 if args.verbose is None else sum(args.verbose)
    log.setLevel(max(10, log.getEffectiveLevel() - 10 * args.verbose))
    manager.run()

if __name__ == "__main__":
    main()
