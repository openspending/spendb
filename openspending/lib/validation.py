from urlparse import urlparse

from openspending.validation.common import mapping
from openspending.validation.common import key
from openspending.validation.predicates import chained, \
    nonempty_string


def valid_url(url):
    parsed = urlparse(url)
    if parsed.scheme.lower() not in ('http', 'https'):
        return "Only HTTP/HTTPS web addresses are supported " \
               "at the moment."
    return True


def source_schema():
    schema = mapping('source')
    schema.add(key('url', validator=chained(
        nonempty_string,
        valid_url
    )))
    return schema
