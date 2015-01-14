from openspending.reference.util import get_csv

data = get_csv('countries')
conv = lambda c: (c['ISO-2'].decode('utf-8'), \
                  c['Country'].decode('utf-8'))
COUNTRIES = dict(map(conv, data))
