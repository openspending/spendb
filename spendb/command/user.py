from spendb.command.util import create_submanager
from spendb.command.util import CommandException

manager = create_submanager(description='User operations')


@manager.command
#@manager.option('username')
def grantadmin(username):
    """ Grant admin privileges to given user """
    from spendb.model import meta as db
    from spendb.model.account import Account

    a = Account.by_name(username)

    if a is None:
        raise CommandException("Account `%s` not found." % username)

    a.admin = True
    db.session.add(a)
    db.session.commit()
