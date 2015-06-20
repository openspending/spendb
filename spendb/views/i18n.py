from spendb.core import babel

from flask import session, request
from babel import Locale


def get_locale():
    if 'locale' in session:
        return Locale.parse(session.get('locale'))
    else:
        requested = request.accept_languages.values()
        requested = [l.replace('-', '_') for l in requested]
        available = map(unicode, babel.list_translations())
        return Locale.negotiate(available, requested)
