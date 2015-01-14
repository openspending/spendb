from openspending.reference.util import get_json

data = get_json('currency')
currencies = data['codelist']['Currency']
CURRENCIES = dict(map(lambda c: (c['code'], (c['name'], c.get('key', False))), \
        currencies))

