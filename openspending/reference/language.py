from openspending.reference.util import get_json

data = get_json('language')
currencies = data['codelist']['Language']
LANGUAGES = dict(map(lambda c: (c['code'], c['name']), currencies))

