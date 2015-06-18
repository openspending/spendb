import os
import requests
import json
import time

DIR = 'os_export/exports'
SPENDB_HOST = os.environ.get('SPENDB_HOST', 'http://spendb.pudo.org')
SPENDB_API_KEY = os.environ.get('SPENDB_API_KEY')

assert SPENDB_API_KEY, 'Please set the SPENDB_API_KEY environment variable'


def make_api_path(*a):
    parts = [SPENDB_HOST, '/api/3/datasets'] + list(a)
    return '/'.join([p.strip('/') for p in parts])

session = requests.Session()
session.headers.update({
    'Authorization': 'apikey %s' % SPENDB_API_KEY
})
json_headers = {
    'Content-type': 'application/json',
    'Accept': 'text/plain'
}


def list_datasets():
    for name in os.listdir(DIR):
        ds_dir = os.path.join(DIR, name)
        with open(os.path.join(ds_dir, 'dataset.json'), 'rb') as fh:
            meta = json.load(fh)
        with open(os.path.join(ds_dir, 'model.json'), 'rb') as fh:
            model = json.load(fh)
        src_file = os.path.join(ds_dir, 'facts.csv')
        yield meta, src_file, model


def load_dataset(metadata, source_file, model):
    name = metadata.get('name')

    # Available metadata fields (name and label are required):
    config = {
        'name': name,
        'label': metadata['label'],
        'private': False,
        'category': metadata['category'],  # 'budget' or 'spending'
        'currency': metadata['currency'],  # e.g. 'USD', 'EUR'
        'languages': metadata['languages'],  # e.g. ['en', 'de']
        'territories': metadata['territories'],  # e.g. ['DE', 'FR']
    }

    # Step 1: Create (or update) the dataset.
    print '[spendb-import] Creating/updating %r' % name
    res = session.get(make_api_path(name))
    if res.status_code == 404:
        # dataset does not exist yet
        res = session.post(make_api_path(), data=json.dumps(config),
                           headers=json_headers)
        assert res.status_code == 200, res.content
    elif res.status_code == 200:
        # update the existing dataset's metadata
        res = session.post(make_api_path(name),
                           data=json.dumps(config),
                           headers=json_headers)
        assert res.status_code == 200, res.content
    else:
        print 'Error accessing dataset: %r' % res.content

    # Step 2: Upload a source data file.
    print '[spendb-import] Uploading %r' % source_file
    upload_url = make_api_path(name, 'sources/upload')
    # Note: there is also /api/3/datasets/<foo>/sources/submit which
    # will accept a simple URL, then attempt to fetch and load that
    # data file. That API call (unlike this one) does not return a
    # source object.

    files = {'file': open(source_file, 'rb')}
    res = session.post(upload_url, files=files)
    assert res.status_code == 200, res.content

    # This is a bit ugly: we need to wait for the source data
    # to be parsed before a data model can be applied.
    runs_url = res.json().get('runs_url')
    while True:
        res = session.get(runs_url)
        runs = res.json().get('results')
        runs = sorted(runs, key=lambda r: r.get('time_start'))
        current_run = runs[-1]
        assert current_run['status'] != 'failed'

        # There are multiple operations, we want to wait for
        # the one related to database loading to complete.
        if current_run['status'] == 'complete' and \
                'database' in current_run['operation']:
            break
        print '[spendb-import] Waiting for data to be loaded...'
        time.sleep(5)

    # Step 3: Map source data columns to OLAP measures and dimensions
    print '[spendb-import] Applying model to dataset %r' % name
    res = session.post(make_api_path(name, 'model'),
                       data=json.dumps(model),
                       headers=json_headers)
    assert res.status_code == 200, res.content

    print '[spendb-import] Done.'


if __name__ == '__main__':
    for meta, src_file, model in list_datasets():
        load_dataset(meta, src_file, model)
