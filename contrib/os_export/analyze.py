import os
import requests
from datetime import datetime
from urlparse import urljoin

INSTANCE = 'https://openspending.org'


def user_get(url, params={}):
    api_key = os.environ.get('OPENSPENDING_APIKEY')
    headers = {'Authorization': 'ApiKey %s' % api_key}
    if not url.startswith('http'):
        url = urljoin(INSTANCE, url)
    params['__'] = datetime.utcnow().isoformat()
    return requests.get(url, params=params,
                        headers=headers)


def get_sources(dataset):
    res = user_get('/%s/sources.json' % dataset['name'])
    for source in res.json():
        print source


def get_datasets():
    res = user_get('/datasets.json')
    for dataset in res.json().get('datasets'):
        print dataset.get('name')
        get_sources(dataset)

    print len(res.json().get('datasets')), 'datasets'


if __name__ == '__main__':
    get_datasets()


