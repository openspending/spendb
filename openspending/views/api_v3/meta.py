import logging

from flask import Blueprint
from apikit import jsonify

from openspending.reference import CURRENCIES, COUNTRIES
from openspending.reference import CATEGORIES, LANGUAGES
from openspending.views.cache import etag_cache_keygen

log = logging.getLogger(__name__)
blueprint = Blueprint('meta_api3', __name__)


def dicts(d):
    for k, v in d.items():
        if isinstance(v, tuple):
            yield {'code': k, 'label': v[0], 'key': v[1]}
        else:
            yield {'code': k, 'label': v}


@blueprint.route('/reference')
def reference_data():
    etag_cache_keygen('england prevails')
    return jsonify({
        'currencies': sorted(dicts(CURRENCIES), key=lambda d: d['label']),
        'languages': sorted(dicts(LANGUAGES), key=lambda d: d['label']),
        'territories': sorted(dicts(COUNTRIES), key=lambda d: d['label']),
        'categories': sorted(dicts(CATEGORIES), key=lambda d: d['label'])
    })
