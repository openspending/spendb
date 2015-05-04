import urllib
import os
import json
import csv
import urlparse
from StringIO import StringIO
from datetime import datetime

from spendb.model.dataset import Dataset
from spendb.core import db


def fixture_file(name):
    """Return a file-like object pointing to a named fixture."""
    return open(fixture_path(name))


def meta_fixture(name):
    meta_fp = fixture_file('meta/' + name + '.json')
    meta = json.load(meta_fp)
    meta_fp.close()
    return meta


def validation_fixture(name):
    model_fp = fixture_file('validation/' + name + '.json')
    model = json.load(model_fp)
    model_fp.close()
    return model


def data_fixture(name):
    return fixture_file('data/' + name + '.csv')


def fixture_path(name):
    """Return the full path to a named fixture.
    Use fixture_file rather than this method wherever possible.
    """
    # Get the directory of this file (helpers is placed in the test directory)
    test_directory = os.path.dirname(__file__)
    # Fixture is a directory in the test directory
    return os.path.join(test_directory, 'fixtures', name)


def csvimport_fixture_path(name, path):
    url = urllib.pathname2url(fixture_path('csv_import/%s/%s' % (name, path)))
    return urlparse.urljoin('file:', url)


def csvimport_fixture_file(name, path):
    try:
        fp = urllib.urlopen(csvimport_fixture_path(name, path))
    except IOError:
        if name == 'default':
            fp = None
        else:
            fp = csvimport_fixture_file('default', path)

    if fp:
        fp = StringIO(fp.read())
    return fp


def csvimport_table(name):
    from messytables import CSVTableSet, type_guess
    from messytables import types_processor, headers_guess
    from messytables import headers_processor, offset_processor
    from spendb.etl.extract import parse_table

    row_set = CSVTableSet(data_fixture(name)).tables[0]
    offset, headers = headers_guess(row_set.sample)
    row_set.register_processor(headers_processor(headers))
    row_set.register_processor(offset_processor(offset + 1))
    types = type_guess(row_set.sample, strict=True)
    row_set.register_processor(types_processor(types))

    rows = []
    for num_rows, (fields, row, samples) in enumerate(parse_table(row_set)):
        rows.append(row)

    return fields, rows


def load_fixture(name, manager=None):
    """ Load fixture data into the database. """
    meta = meta_fixture(name)
    dataset = Dataset(meta)
    dataset.updated_at = datetime.utcnow()
    if manager is not None:
        dataset.managers.append(manager)
    fields, rows = csvimport_table(name)
    dataset.fields = fields
    db.session.add(dataset)
    db.session.commit()
    dataset.fact_table.create()
    dataset.fact_table.load_iter(rows)
    return dataset


def make_account(name='test', fullname='Test User',
                 email='test@example.com', twitter='testuser',
                 admin=False):
    from spendb.model.account import Account

    # First see if the account already exists and if so, return it
    account = Account.by_name(name)
    if account:
        return account

    # Account didn't exist so we create it and return it
    account = Account()
    account.name = name
    account.fullname = fullname
    account.email = email
    account.twitter_handle = twitter
    account.admin = admin
    db.session.add(account)
    db.session.commit()
    return account


def init_db(app):
    db.create_all(app=app)


def clean_db(app):
    db.session.rollback()
    db.drop_all(app=app)
