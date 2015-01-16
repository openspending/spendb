from openspending.command.util import create_submanager
from openspending.command.util import CommandException

from openspending.core import db
from openspending.model.account import Account

manager = create_submanager(description='User operations')


@manager.command
#@manager.option('username')
def grantadmin(username):
    """ Grant admin privileges to given user """

    a = Account.by_name(username)

    if a is None:
        raise CommandException("Account `%s` not found." % username)

    a.admin = True
    db.session.add(a)
    db.session.commit()
