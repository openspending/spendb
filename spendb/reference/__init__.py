from spendb.reference.util import get_csv, get_json

CATEGORIES = {
    "budget": "Budget",
    "spending": "Expenditure",
    "other": "Other"
}

data = get_csv('countries')
conv = lambda c: (c['ISO-2'].decode('utf-8'),
                  c['Country'].decode('utf-8'))
COUNTRIES = dict(map(conv, data))

data = get_json('currency')
currencies = data['codelist']['Currency']
CURRENCIES = dict(map(lambda c: (c['code'], (c['name'], c.get('key', False))),
                  currencies))

data = get_json('language')
currencies = data['codelist']['Language']
LANGUAGES = dict(map(lambda c: (c['code'], c['name']), currencies))
