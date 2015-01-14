import urllib
import os
import shutil
import json
import csv
import urlparse
from StringIO import StringIO
from datetime import datetime

from openspending.model.dataset import Dataset
from openspending.core import db
from openspending.lib import solr_util as solr


def fixture_file(name):
    """Return a file-like object pointing to a named fixture."""
    return open(fixture_path(name))


def model_fixture(name):
    model_fp = fixture_file('model/' + name + '.json')
    model = json.load(model_fp)
    model_fp.close()
    return model


def validation_fixture(name):
    model_fp = fixture_file('validation/' + name + '.json')
    model = json.load(model_fp)
    model_fp.close()
    return model


def data_fixture(name):
    return fixture_file('data/' + name + '.csv')


def fixture_path(name):
    """
    Return the full path to a named fixture.

    Use fixture_file rather than this method wherever possible.
    """
    # Get the directory of this file (helpers is placed in the test directory)
    test_directory = os.path.dirname(__file__)
    # Fixture is a directory in the test directory
    return os.path.join(test_directory, 'fixtures', name)


CPI = []
for row in csv.DictReader(fixture_file('cpi.csv')):
    row['CPI'] = float(row['CPI'])
    row['Year'] = datetime(year=int(row['Year']), month=1, day=1).date()
    CPI.append(row)


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
    from messytables import CSVTableSet
    from loadkit.transform import parse_table
    table_set = CSVTableSet(data_fixture(name))
    row_set = table_set.tables[0]
    rows = []

    def save_row(row):
        rows.append(row)
    
    num_rows, fields = parse_table(row_set, save_row)
    return fields, rows


def load_fixture(name, manager=None):
    """
    Load fixture data into the database.
    """
    model = model_fixture(name)
    dataset = Dataset(model)
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


#def load_dataset(dataset):
#    fields, rows = csvimport_table('simple')
    #dataset.data['mapping'] = model = model_fixture('simple')
#    dataset.fields = fields
#    dataset.fact_table.load_iter(rows)


def make_account(name='test', fullname='Test User',
                 email='test@example.com', twitter='testuser',
                 admin=False):
    from openspending.model.account import Account

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
    shutil.rmtree(app.config.get('UPLOADS_DEFAULT_DEST'))


def clean_solr():
    '''Clean all entries from Solr.'''
    s = solr.get_connection()
    s.delete_query('*:*')
    s.commit()


def clean_and_reindex_solr():
    '''Clean Solr and reindex all entries in the database.'''
    clean_solr()
    for dataset in db.session.query(Dataset):
        solr.build_index(dataset.name)
